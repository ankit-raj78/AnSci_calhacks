"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Upload, FileText, Paperclip, Send, Play, SkipForward } from "lucide-react"
import { ApiService, AnimationResponse } from "@/lib/api"

type AppState = "input" | "processing" | "results"

interface AnimationScope {
  id: string;
  name: string;
  description: string;
}

const ANIMATION_SCOPES: AnimationScope[] = [
  {
    id: "high-level",
    name: "High-Level Summary",
    description: "Key findings and conclusions"
  },
  {
    id: "core-concepts",
    name: "Core Concepts", 
    description: "Main ideas and methodologies"
  },
  {
    id: "full-walkthrough",
    name: "Full Walkthrough",
    description: "Complete detailed explanation"
  }
];

export default function AppPage() {
  const [state, setState] = useState<AppState>("input")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedScope, setSelectedScope] = useState<string>("core-concepts")
  const [chatMessage, setChatMessage] = useState("")
  const [animationResult, setAnimationResult] = useState<AnimationResponse | null>(null)
  const [error, setError] = useState<string>("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && file.type === "application/pdf") {
      setSelectedFile(file)
      setError("")
    } else if (file) {
      setError("Please select a PDF file")
    }
  }

  const handleFileDrop = (event: React.DragEvent) => {
    event.preventDefault()
    const file = event.dataTransfer.files[0]
    if (file && file.type === "application/pdf") {
      setSelectedFile(file)
      setError("")
    } else if (file) {
      setError("Please select a PDF file")
    }
  }

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault()
  }

  const handleGenerate = async () => {
    if (!selectedFile) return

    setState("processing")
    setError("")

    try {
      const scope = ANIMATION_SCOPES.find(s => s.id === selectedScope)?.name || "Core Concepts"
      const result = await ApiService.uploadFile(selectedFile, scope)
      setAnimationResult(result)
      setState("results")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate animation")
      setState("input")
    }
  }

  if (state === "input") {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-6">
        <div className="w-full max-w-2xl">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-light text-stone-900 mb-4">Let's create your animation</h1>
          </div>

          {/* File Upload */}
          <div className="mb-8">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              className="hidden"
            />
            <div
              className="border-2 border-dashed border-gray-200 rounded-2xl p-12 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-colors"
              onClick={() => fileInputRef.current?.click()}
              onDrop={handleFileDrop}
              onDragOver={handleDragOver}
            >
              {selectedFile ? (
                <div className="flex items-center justify-center space-x-3">
                  <FileText className="w-8 h-8 text-blue-500" />
                  <div>
                    <p className="font-medium text-stone-900">{selectedFile.name}</p>
                    <p className="text-sm text-gray-500">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                </div>
              ) : (
                <div>
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg text-gray-600 mb-2">Drop your PDF here</p>
                  <p className="text-sm text-gray-400">or click to browse</p>
                </div>
              )}
            </div>
            {error && (
              <p className="text-red-500 text-sm mt-2">{error}</p>
            )}
          </div>

          {/* Animation Scope */}
          <div className="mb-8">
            <h3 className="text-lg font-medium text-stone-900 mb-4">Animation Scope</h3>
            <div className="grid gap-3">
              {ANIMATION_SCOPES.map((scope) => (
                <button
                  key={scope.id}
                  onClick={() => setSelectedScope(scope.id)}
                  className={`p-4 rounded-xl border-2 text-left transition-colors ${
                    selectedScope === scope.id
                      ? "border-blue-300 bg-blue-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <div className="font-medium text-stone-900">{scope.name}</div>
                  <div className="text-sm text-gray-500">{scope.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Generate Button */}
          <Button
            onClick={handleGenerate}
            disabled={!selectedFile}
            size="lg"
            className="w-full bg-blue-300 text-white hover:bg-blue-400 disabled:bg-gray-200 disabled:text-gray-400"
          >
            Generate Animation
          </Button>
        </div>
      </div>
    )
  }

  if (state === "processing") {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-6">
        <div className="w-full max-w-md text-center">
          <div className="mb-8">
            <div className="w-16 h-16 border-4 border-blue-100 border-t-blue-300 rounded-full animate-spin mx-auto mb-6"></div>
            <h2 className="text-2xl font-light text-stone-900 mb-2">Analyzing your paper...</h2>
            <p className="text-gray-600">This may take a few minutes</p>
          </div>

          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-5 h-5 rounded-full bg-blue-300 flex items-center justify-center">
                <div className="w-2 h-2 bg-white rounded-full"></div>
              </div>
              <span className="text-sm text-stone-900">Parsing PDF</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-5 h-5 rounded-full bg-blue-300 flex items-center justify-center">
                <div className="w-2 h-2 bg-white rounded-full"></div>
              </div>
              <span className="text-sm text-stone-900">Identifying key concepts</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-5 h-5 rounded-full bg-gray-200"></div>
              <span className="text-sm text-gray-500">Rendering scenes</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-5 h-5 rounded-full bg-gray-200"></div>
              <span className="text-sm text-gray-500">Generating animation</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="grid lg:grid-cols-3 h-screen">
        {/* Main Content - Video Player */}
        <div className="lg:col-span-2 p-6 flex flex-col">
          <div className="flex-1">
            {animationResult && animationResult.video_urls.length > 0 ? (
              <div className="bg-stone-900 rounded-2xl aspect-video flex items-center justify-center mb-6">
                <video
                  controls
                  className="w-full h-full rounded-2xl"
                  src={ApiService.getVideoUrl(animationResult.video_urls[0])}
                >
                  Your browser does not support the video tag.
                </video>
              </div>
            ) : (
              <div className="bg-stone-900 rounded-2xl aspect-video flex items-center justify-center mb-6">
                <div className="text-center text-white">
                  <Play className="w-16 h-16 mx-auto mb-4 opacity-80" />
                  <p className="text-lg">Your Animation is Ready</p>
                </div>
              </div>
            )}

            {/* Scene Breakdown */}
            <div>
              <h3 className="text-lg font-medium text-stone-900 mb-4">Scene Breakdown</h3>
              <div className="space-y-2">
                <button className="w-full flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:bg-blue-50 text-left transition-colors">
                  <div className="flex items-center space-x-3">
                    <SkipForward className="w-4 h-4 text-gray-400" />
                    <span className="font-medium text-stone-900">Scene 1: Introduction</span>
                  </div>
                  <span className="text-sm text-gray-500">0:30</span>
                </button>
                <button className="w-full flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:bg-blue-50 text-left transition-colors">
                  <div className="flex items-center space-x-3">
                    <SkipForward className="w-4 h-4 text-gray-400" />
                    <span className="font-medium text-stone-900">Scene 2: Methodology Overview</span>
                  </div>
                  <span className="text-sm text-gray-500">1:15</span>
                </button>
                <button className="w-full flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:bg-blue-50 text-left transition-colors">
                  <div className="flex items-center space-x-3">
                    <SkipForward className="w-4 h-4 text-gray-400" />
                    <span className="font-medium text-stone-900">Scene 3: Key Findings</span>
                  </div>
                  <span className="text-sm text-gray-500">2:00</span>
                </button>
                <button className="w-full flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:bg-blue-50 text-left transition-colors">
                  <div className="flex items-center space-x-3">
                    <SkipForward className="w-4 h-4 text-gray-400" />
                    <span className="font-medium text-stone-900">Scene 4: Conclusions</span>
                  </div>
                  <span className="text-sm text-gray-500">0:45</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Chat Interface */}
        <div className="border-l border-gray-100 p-6 flex flex-col">
          <div className="mb-6">
            <h2 className="text-xl font-medium text-stone-900 text-center">What would you like to refine?</h2>
          </div>

          <div className="flex-1 mb-6">
            <div className="text-center text-gray-500 text-sm">Ask anything about your animation...</div>
          </div>

          {/* Chat Input */}
          <div className="border border-gray-200 rounded-2xl p-4">
            <Input
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              placeholder="Ask anything..."
              className="border-0 p-0 text-base focus-visible:ring-0 mb-4"
            />

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900 transition-colors">
                  <Paperclip className="w-4 h-4" />
                  <span>Attach</span>
                </button>
              </div>

              <Button
                disabled={!chatMessage.trim()}
                size="sm"
                className="bg-blue-300 text-white hover:bg-blue-400 disabled:bg-gray-200"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
