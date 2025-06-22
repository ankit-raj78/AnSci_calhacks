"""
Synchronization Validator
Validates and corrects audio-visual synchronization
"""

import logging
import json
import subprocess
from typing import Dict, List, Optional, Any, Tuple
import os
import re

logger = logging.getLogger(__name__)

class SyncValidator:
    def __init__(self):
        self.confidence_threshold = float(os.getenv('SYNC_CONFIDENCE_THRESHOLD', '0.95'))
        self.timing_tolerance_ms = int(os.getenv('TIMING_TOLERANCE_MS', '100'))
        self.max_correction_attempts = int(os.getenv('MAX_SYNC_CORRECTION_ATTEMPTS', '3'))
        logger.info("Sync validator initialized")

    def validate_sync(self, manim_code: str, audio_data: Dict[str, Any], 
                     sync_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate synchronization between animation and audio
        
        Args:
            manim_code: Generated Manim Python code
            audio_data: Audio file information including duration
            sync_points: Expected synchronization points
        
        Returns:
            Validation result with confidence score and corrections
        """
        try:
            # Extract timing information from Manim code
            animation_timing = self._extract_animation_timing(manim_code)
            audio_duration = audio_data.get('duration', 0)
            
            # Validate total duration match
            duration_diff = abs(animation_timing['total_duration'] - audio_duration)
            duration_score = max(0, 1 - (duration_diff / audio_duration)) if audio_duration > 0 else 0
            
            # Validate sync points
            sync_score, sync_issues = self._validate_sync_points(
                animation_timing, 
                sync_points, 
                audio_duration
            )
            
            # Calculate overall confidence
            confidence = (duration_score * 0.4 + sync_score * 0.6)
            
            # Generate corrections if needed
            corrections = []
            if confidence < self.confidence_threshold:
                corrections = self._generate_corrections(
                    animation_timing, 
                    audio_data, 
                    sync_points, 
                    sync_issues
                )
            
            result = {
                'confidence': confidence,
                'duration_score': duration_score,
                'sync_score': sync_score,
                'timing_data': animation_timing,
                'audio_duration': audio_duration,
                'duration_difference': duration_diff,
                'sync_issues': sync_issues,
                'corrections': corrections,
                'valid': confidence >= self.confidence_threshold
            }
            
            logger.info(f"Sync validation complete: {confidence:.3f} confidence")
            return result
            
        except Exception as e:
            logger.error(f"Error in sync validation: {e}")
            return {
                'confidence': 0.0,
                'valid': False,
                'error': str(e),
                'corrections': []
            }

    def _extract_animation_timing(self, manim_code: str) -> Dict[str, Any]:
        """Extract timing information from Manim code"""
        try:
            # Parse wait() calls and animation durations
            wait_pattern = r'self\.wait\(([^)]+)\)'
            play_pattern = r'self\.play\([^)]+(?:,\s*run_time\s*=\s*([^,)]+))?'
            
            wait_times = []
            play_times = []
            
            # Extract wait times
            for match in re.finditer(wait_pattern, manim_code):
                try:
                    wait_time = float(eval(match.group(1)))  # Evaluate expression like "2" or "1.5"
                    wait_times.append(wait_time)
                except:
                    wait_times.append(1.0)  # Default wait time
            
            # Extract play/animation times
            for match in re.finditer(play_pattern, manim_code):
                if match.group(1):  # Has explicit run_time
                    try:
                        play_time = float(eval(match.group(1)))
                        play_times.append(play_time)
                    except:
                        play_times.append(1.0)  # Default animation time
                else:
                    play_times.append(1.0)  # Default animation time
            
            # Calculate total duration
            total_duration = sum(wait_times) + sum(play_times)
            
            # Create timing breakdown
            timing_events = []
            current_time = 0
            
            # This is a simplified parsing - in production you'd want more sophisticated analysis
            lines = manim_code.split('\n')
            for i, line in enumerate(lines):
                if 'self.wait(' in line:
                    wait_match = re.search(wait_pattern, line)
                    if wait_match:
                        duration = float(eval(wait_match.group(1))) if wait_match.group(1) else 1.0
                        timing_events.append({
                            'type': 'wait',
                            'start_time': current_time,
                            'duration': duration,
                            'line': i + 1
                        })
                        current_time += duration
                
                elif 'self.play(' in line:
                    play_match = re.search(play_pattern, line)
                    duration = 1.0  # Default
                    if play_match and play_match.group(1):
                        duration = float(eval(play_match.group(1)))
                    
                    timing_events.append({
                        'type': 'animation',
                        'start_time': current_time,
                        'duration': duration,
                        'line': i + 1
                    })
                    current_time += duration
            
            return {
                'total_duration': total_duration,
                'wait_times': wait_times,
                'play_times': play_times,
                'timing_events': timing_events,
                'event_count': len(timing_events)
            }
            
        except Exception as e:
            logger.error(f"Error extracting animation timing: {e}")
            return {
                'total_duration': 0,
                'wait_times': [],
                'play_times': [],
                'timing_events': [],
                'event_count': 0,
                'error': str(e)
            }

    def _validate_sync_points(self, animation_timing: Dict[str, Any], 
                            sync_points: List[Dict[str, Any]], 
                            audio_duration: float) -> Tuple[float, List[Dict[str, Any]]]:
        """Validate specific synchronization points"""
        if not sync_points:
            return 1.0, []  # No sync points to validate
        
        issues = []
        valid_points = 0
        
        for sync_point in sync_points:
            expected_time = sync_point.get('time', 0)
            sync_name = sync_point.get('name', 'unknown')
            
            # Find closest animation event
            closest_event = None
            min_distance = float('inf')
            
            for event in animation_timing.get('timing_events', []):
                distance = abs(event['start_time'] - expected_time)
                if distance < min_distance:
                    min_distance = distance
                    closest_event = event
            
            # Check if sync point is within tolerance
            tolerance_seconds = self.timing_tolerance_ms / 1000.0
            
            if closest_event and min_distance <= tolerance_seconds:
                valid_points += 1
            else:
                issues.append({
                    'sync_point': sync_name,
                    'expected_time': expected_time,
                    'closest_event_time': closest_event['start_time'] if closest_event else None,
                    'distance': min_distance,
                    'type': 'timing_mismatch'
                })
        
        sync_score = valid_points / len(sync_points) if sync_points else 1.0
        return sync_score, issues

    def _generate_corrections(self, animation_timing: Dict[str, Any], 
                            audio_data: Dict[str, Any], 
                            sync_points: List[Dict[str, Any]], 
                            sync_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate timing corrections to improve synchronization"""
        corrections = []
        
        # Duration correction
        audio_duration = audio_data.get('duration', 0)
        animation_duration = animation_timing.get('total_duration', 0)
        
        if abs(animation_duration - audio_duration) > 0.5:  # 500ms tolerance
            duration_correction = {
                'type': 'duration_adjustment',
                'current_duration': animation_duration,
                'target_duration': audio_duration,
                'adjustment_factor': audio_duration / animation_duration if animation_duration > 0 else 1.0,
                'description': f"Adjust total duration from {animation_duration:.2f}s to {audio_duration:.2f}s"
            }
            corrections.append(duration_correction)
        
        # Sync point corrections
        for issue in sync_issues:
            if issue['type'] == 'timing_mismatch':
                correction = {
                    'type': 'sync_point_adjustment',
                    'sync_point': issue['sync_point'],
                    'current_time': issue['closest_event_time'],
                    'target_time': issue['expected_time'],
                    'adjustment': issue['expected_time'] - (issue['closest_event_time'] or 0),
                    'description': f"Move {issue['sync_point']} by {issue['distance']:.2f}s"
                }
                corrections.append(correction)
        
        # Animation speed corrections
        if len(sync_issues) > len(sync_points) * 0.5:  # More than 50% of sync points have issues
            speed_correction = {
                'type': 'global_speed_adjustment',
                'description': "Adjust overall animation speed to better match audio",
                'recommended_factor': audio_duration / animation_duration if animation_duration > 0 else 1.0
            }
            corrections.append(speed_correction)
        
        return corrections

    def apply_corrections(self, manim_code: str, corrections: List[Dict[str, Any]]) -> str:
        """Apply timing corrections to Manim code"""
        try:
            corrected_code = manim_code
            
            for correction in corrections:
                if correction['type'] == 'duration_adjustment':
                    factor = correction.get('adjustment_factor', 1.0)
                    corrected_code = self._apply_duration_correction(corrected_code, factor)
                
                elif correction['type'] == 'sync_point_adjustment':
                    adjustment = correction.get('adjustment', 0)
                    corrected_code = self._apply_sync_point_correction(corrected_code, adjustment)
                
                elif correction['type'] == 'global_speed_adjustment':
                    factor = correction.get('recommended_factor', 1.0)
                    corrected_code = self._apply_speed_correction(corrected_code, factor)
            
            logger.info(f"Applied {len(corrections)} timing corrections")
            return corrected_code
            
        except Exception as e:
            logger.error(f"Error applying corrections: {e}")
            return manim_code  # Return original if correction fails

    def _apply_duration_correction(self, code: str, factor: float) -> str:
        """Apply global duration scaling to all timing in the code"""
        def scale_timing(match):
            try:
                original_value = float(eval(match.group(1)))
                scaled_value = original_value * factor
                return f"{match.group(0).split('(')[0]}({scaled_value:.2f})"
            except:
                return match.group(0)
        
        # Scale wait times
        code = re.sub(r'self\.wait\(([^)]+)\)', scale_timing, code)
        
        # Scale run_time parameters
        code = re.sub(r'run_time\s*=\s*([^,)]+)', 
                     lambda m: f"run_time={float(eval(m.group(1))) * factor:.2f}", code)
        
        return code

    def _apply_sync_point_correction(self, code: str, adjustment: float) -> str:
        """Apply specific timing adjustments for sync points"""
        # This is simplified - you'd need more sophisticated code analysis
        # to identify which specific timing to adjust for each sync point
        lines = code.split('\n')
        
        # Find and adjust the first wait time (simplified approach)
        for i, line in enumerate(lines):
            if 'self.wait(' in line and adjustment != 0:
                wait_match = re.search(r'self\.wait\(([^)]+)\)', line)
                if wait_match:
                    try:
                        current_wait = float(eval(wait_match.group(1)))
                        new_wait = max(0.1, current_wait + adjustment)  # Minimum 0.1s wait
                        lines[i] = re.sub(r'self\.wait\([^)]+\)', f'self.wait({new_wait:.2f})', line)
                        break
                    except:
                        continue
        
        return '\n'.join(lines)

    def _apply_speed_correction(self, code: str, factor: float) -> str:
        """Apply global speed correction by scaling all timing"""
        return self._apply_duration_correction(code, 1.0 / factor)
