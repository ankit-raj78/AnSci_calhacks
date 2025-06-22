"use client"

import { Button } from "@/components/ui/button"
import { ArrowRight, Upload, Settings, Play, FileText, Video } from "lucide-react"
import Link from "next/link"
import Image from "next/image"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white font-sans">
      {/* Navigation */}
      <nav className="border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-2xl font-semibold text-stone-900">AnSci</div>
            <Link href="/app">
              <Button variant="outline" className="bg-white text-stone-900 border-gray-200 hover:bg-gray-50">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-24">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-6xl font-medium text-stone-900 mb-6 leading-tight">
            <span className="text-blue-300 font-medium">Now Papers</span>{" "}
            <span className="font-medium text-blue-300">Explain Themselves</span>
          </h1>
          <p className="text-xl text-gray-600 mb-12 leading-relaxed max-w-2xl mx-auto font-light tracking-wide">
            AnSci uses AI to transform dense research papers into clear, engaging animations. <br />
            Understand complex topics in minutes.
          </p>

          {/* Visual Representation */}
          <div className="mb-12 p-8 bg-blue-50 rounded-2xl border border-blue-100">
            <div className="flex items-center justify-center space-x-8">
              <div className="text-center">
                <div className="w-24 h-32 bg-white border-2 border-gray-200 rounded-lg flex items-center justify-center mb-4">
                  <FileText className="w-8 h-8 text-gray-400" />
                </div>
                <p className="text-sm text-gray-500">Dense Research Paper</p>
              </div>
              <ArrowRight className="w-8 h-8 text-gray-400" />
              <div className="text-center">
                <div className="w-24 h-32 bg-gradient-to-br from-blue-100 to-blue-200 border-2 border-blue-200 rounded-lg flex items-center justify-center mb-4">
                  <Video className="w-8 h-8 text-blue-500" />
                </div>
                <p className="text-sm text-gray-500">Clear Animation</p>
              </div>
            </div>
          </div>

          <Link href="/app">
            <Button size="lg" className="bg-blue-300 text-white hover:bg-blue-400 px-8 py-4 text-lg">
              Create Your First Animation
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* How It Works */}
      <section className="bg-blue-50 py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-light text-stone-900 mb-4">How It Works</h2>
            <p className="text-xl text-gray-500 leading-relaxed max-w-2xl mx-auto font-light tracking-wide">
              Three simple steps to transform your research
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            <div className="text-center">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm">
                <Upload className="w-8 h-8 text-gray-700" />
              </div>
              <h3 className="text-xl font-medium text-stone-900 mb-3">Upload</h3>
              <p className="text-base text-gray-600 leading-relaxed">
                Provide research paper in PDF format
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm">
                <Settings className="w-8 h-8 text-gray-700" />
              </div>
              <h3 className="text-xl font-medium text-stone-900 mb-3">Customize</h3>
              <p className="text-base text-gray-600 leading-relaxed">
                Select the scope for your animation
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm">
                <Play className="w-8 h-8 text-gray-700" />
              </div>
              <h3 className="text-xl font-medium text-stone-900 mb-3">Animate</h3>
              <p className="text-base text-gray-600 leading-relaxed">
                Receive a complete video explanation, ready to refine or share
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Showcase */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-light text-stone-900 mb-4">Before & After</h2>
            <p className="text-xl text-gray-500 leading-relaxed max-w-2xl mx-auto font-light tracking-wide">
              See how complex research becomes clear
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12 items-start">
            <div>
              <h3 className="text-lg font-medium text-stone-900 mb-4">Before: Dense Text</h3>
              <div className="bg-white border-2 border-gray-200 rounded-lg p-4 min-h-96 flex items-center justify-center">
                <Image 
                  src="/demo/paper.png" 
                  alt="Research paper with dense text" 
                  width={800}
                  height={600}
                  className="max-w-full max-h-full object-contain rounded-lg shadow-md"
                  priority
                />
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium text-stone-900 mb-4">After: Clear Animation</h3>
              <div className="bg-white border-2 border-gray-200 rounded-lg p-4 min-h-96 flex items-center justify-center">
                <Image 
                  src="/demo/animation.png" 
                  alt="Clear animated visualization" 
                  width={800}
                  height={600}
                  className="max-w-full max-h-full object-contain rounded-lg shadow-md"
                  priority
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="bg-blue-50 py-16"> 
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-light text-stone-900 mb-6">
            Ready to go from static text to dynamic illustrations?
          </h2>

          <Link href="/app" className="inline-block"> 
            <Button
              size="lg"
              className="bg-white text-stone-900 hover:bg-gray-100 px-6 py-3 text-base"
            >
              Start Visualizing
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  )
}
