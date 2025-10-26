import { CheckCircle2 } from "lucide-react"

export default function AboutSection() {
  return (
    <section className="py-20 sm:py-32 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div className="space-y-6">
            <div className="space-y-2">
              <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 text-balance">About the AI Agent</h2>
              <div className="w-12 h-1 bg-gradient-to-r from-blue-600 to-blue-400 rounded-full"></div>
            </div>

            <p className="text-lg text-gray-600 leading-relaxed">
              AI Agent for Social Media Marketing is an intelligent assistant built to help small and tiny business
              owners professionally manage their Facebook marketing at low cost. It analyzes customer messages, monitors
              competitors, generates promotional posts, and suggests ad campaigns — all in one dashboard.
            </p>

            <div className="space-y-3 pt-4">
              {[
                "Powered by advanced AI and machine learning",
                "Integrates seamlessly with Meta's Graph API",
                "Real-time analytics and insights",
                "24/7 automated monitoring and optimization",
              ].map((feature, index) => (
                <div key={index} className="flex items-start gap-3">
                  <CheckCircle2 className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700 font-medium">{feature}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Right Visual */}
          <div className="hidden lg:flex justify-center">
            <div className="relative w-full max-w-md">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-8 border border-blue-200">
                <div className="space-y-6">
                  {/* Graphs Icon */}
                  <div className="flex justify-center">
                    <div className="w-20 h-20 bg-blue-600 rounded-2xl flex items-center justify-center">
                      <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                        />
                      </svg>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-blue-600">10M+</div>
                      <div className="text-xs text-gray-600 mt-1">Messages Analyzed</div>
                    </div>
                    <div className="bg-white rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-blue-600">500+</div>
                      <div className="text-xs text-gray-600 mt-1">Active Businesses</div>
                    </div>
                    <div className="bg-white rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-blue-600">99.9%</div>
                      <div className="text-xs text-gray-600 mt-1">Uptime</div>
                    </div>
                    <div className="bg-white rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-blue-600">24/7</div>
                      <div className="text-xs text-gray-600 mt-1">Support</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
