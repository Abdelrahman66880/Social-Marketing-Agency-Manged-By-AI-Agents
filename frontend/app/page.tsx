"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ArrowRight, BarChart3, MessageSquare, Zap } from "lucide-react"

export default function AuthPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [activeTab, setActiveTab] = useState("login")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setTimeout(() => setIsLoading(false), 1000)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
        {/* Left Side - Auth Forms */}
        <div className="flex flex-col justify-center">
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">AI Agent</h1>
            </div>
            <p className="text-gray-600 text-sm">Social Media Marketing Automation</p>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-6 bg-gray-100">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="register">Sign Up</TabsTrigger>
            </TabsList>

            {/* Login Tab */}
            <TabsContent value="login" className="space-y-4">
              <Card className="border-0 shadow-lg bg-white rounded-2xl p-6">
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="login-email" className="text-gray-700 font-medium">
                      Email Address
                    </Label>
                    <Input
                      id="login-email"
                      type="email"
                      placeholder="you@example.com"
                      className="rounded-lg border-gray-200 bg-gray-50 focus:bg-white h-11"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="login-password" className="text-gray-700 font-medium">
                      Password
                    </Label>
                    <Input
                      id="login-password"
                      type="password"
                      placeholder="••••••••"
                      className="rounded-lg border-gray-200 bg-gray-50 focus:bg-white h-11"
                      required
                    />
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" className="rounded border-gray-300" />
                      <span className="text-gray-600">Remember me</span>
                    </label>
                    <a href="#" className="text-blue-600 hover:text-blue-700 font-medium">
                      Forgot password?
                    </a>
                  </div>

                  <Button
                    type="submit"
                    disabled={isLoading}
                    className="w-full h-11 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
                  >
                    {isLoading ? "Signing in..." : "Sign In"}
                    {!isLoading && <ArrowRight className="w-4 h-4" />}
                  </Button>
                </form>
              </Card>
            </TabsContent>

            {/* Register Tab */}
            <TabsContent value="register" className="space-y-4">
              <Card className="border-0 shadow-lg bg-white rounded-2xl p-6">
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-2">
                      <Label htmlFor="first-name" className="text-gray-700 font-medium">
                        First Name
                      </Label>
                      <Input
                        id="first-name"
                        placeholder="John"
                        className="rounded-lg border-gray-200 bg-gray-50 focus:bg-white h-11"
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="last-name" className="text-gray-700 font-medium">
                        Last Name
                      </Label>
                      <Input
                        id="last-name"
                        placeholder="Doe"
                        className="rounded-lg border-gray-200 bg-gray-50 focus:bg-white h-11"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="register-email" className="text-gray-700 font-medium">
                      Email Address
                    </Label>
                    <Input
                      id="register-email"
                      type="email"
                      placeholder="you@example.com"
                      className="rounded-lg border-gray-200 bg-gray-50 focus:bg-white h-11"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="company" className="text-gray-700 font-medium">
                      Business Name
                    </Label>
                    <Input
                      id="company"
                      placeholder="Your Business"
                      className="rounded-lg border-gray-200 bg-gray-50 focus:bg-white h-11"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="register-password" className="text-gray-700 font-medium">
                      Password
                    </Label>
                    <Input
                      id="register-password"
                      type="password"
                      placeholder="••••••••"
                      className="rounded-lg border-gray-200 bg-gray-50 focus:bg-white h-11"
                      required
                    />
                  </div>

                  <label className="flex items-start gap-2 cursor-pointer">
                    <input type="checkbox" className="rounded border-gray-300 mt-1" required />
                    <span className="text-gray-600 text-sm">
                      I agree to the{" "}
                      <a href="#" className="text-blue-600 hover:text-blue-700 font-medium">
                        Terms of Service
                      </a>{" "}
                      and{" "}
                      <a href="#" className="text-blue-600 hover:text-blue-700 font-medium">
                        Privacy Policy
                      </a>
                    </span>
                  </label>

                  <Button
                    type="submit"
                    disabled={isLoading}
                    className="w-full h-11 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
                  >
                    {isLoading ? "Creating account..." : "Create Account"}
                    {!isLoading && <ArrowRight className="w-4 h-4" />}
                  </Button>
                </form>
              </Card>
            </TabsContent>
          </Tabs>

          <p className="text-center text-gray-600 text-sm mt-6">
            {activeTab === "login" ? "Don't have an account? " : "Already have an account? "}
            <button
              onClick={() => setActiveTab(activeTab === "login" ? "register" : "login")}
              className="text-blue-600 hover:text-blue-700 font-semibold"
            >
              {activeTab === "login" ? "Sign up" : "Sign in"}
            </button>
          </p>
        </div>

        {/* Right Side - Feature Preview */}
        <div className="hidden lg:flex flex-col justify-center">
          <Card className="border-0 shadow-2xl bg-white rounded-2xl overflow-hidden">
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 p-6 text-white">
              <h2 className="text-2xl font-bold mb-2">AI-Powered Marketing</h2>
              <p className="text-blue-100">Automate your Facebook campaigns with intelligent insights</p>
            </div>

            <div className="p-8 space-y-6">
              {/* Analytics Preview */}
              <div className="space-y-3">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <BarChart3 className="w-5 h-5 text-blue-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900">Real-Time Analytics</h3>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Campaign Performance</span>
                    <span className="text-sm font-semibold text-green-600">+24.5%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-blue-600 to-blue-500 h-2 rounded-full"
                      style={{ width: "78%" }}
                    ></div>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Engagement Rate</span>
                    <span className="text-sm font-semibold text-green-600">+12.3%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-blue-400 h-2 rounded-full"
                      style={{ width: "65%" }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* AI Chatbot Preview */}
              <div className="space-y-3 pt-4 border-t border-gray-200">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <MessageSquare className="w-5 h-5 text-blue-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900">AI Assistant</h3>
                </div>
                <div className="space-y-3 bg-gray-50 rounded-lg p-4">
                  <div className="flex justify-end">
                    <div className="bg-blue-600 text-white rounded-2xl rounded-tr-none px-4 py-2 text-sm max-w-xs">
                      Create a campaign for summer sale
                    </div>
                  </div>
                  <div className="flex justify-start">
                    <div className="bg-gray-200 text-gray-900 rounded-2xl rounded-tl-none px-4 py-2 text-sm max-w-xs">
                      I'll create an optimized campaign targeting your audience...
                    </div>
                  </div>
                </div>
              </div>

              {/* Key Features */}
              <div className="space-y-2 pt-4 border-t border-gray-200">
                <div className="flex items-center gap-2 text-sm text-gray-700">
                  <div className="w-1.5 h-1.5 bg-blue-600 rounded-full"></div>
                  <span>Automated ad optimization</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-700">
                  <div className="w-1.5 h-1.5 bg-blue-600 rounded-full"></div>
                  <span>24/7 AI monitoring</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-700">
                  <div className="w-1.5 h-1.5 bg-blue-600 rounded-full"></div>
                  <span>Detailed performance reports</span>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
