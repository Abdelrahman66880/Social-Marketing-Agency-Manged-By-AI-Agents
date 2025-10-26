import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowRight, Facebook } from "lucide-react"

export default function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-blue-100 py-20 sm:py-32">
      {/* Decorative gradient mesh background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-blue-100 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div className="flex flex-col justify-center space-y-8">
            <div className="space-y-4">
              <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 leading-tight text-balance">
                Automate Your Facebook Marketing with AI
              </h1>
              <p className="text-xl text-gray-600 leading-relaxed text-balance">
                Save time, understand your audience, and grow your sales using smart recommendations and automation.
                Perfect for small business owners.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/dashboard">
                <Button className="w-full sm:w-auto h-12 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-lg flex items-center justify-center gap-2 text-base">
                  Go to Dashboard
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </Link>
              <Button
                variant="outline"
                className="w-full sm:w-auto h-12 border-2 border-blue-600 text-blue-600 hover:bg-blue-50 font-semibold rounded-lg flex items-center justify-center gap-2 text-base bg-transparent"
              >
                <Facebook className="w-5 h-5" />
                Connect Facebook Page
              </Button>
            </div>

            {/* Trust Indicators */}
            <div className="flex flex-wrap gap-6 pt-4">
              <div className="flex items-center gap-2">
                <div className="flex -space-x-2">
                  {[1, 2, 3].map((i) => (
                    <div
                      key={i}
                      className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 border-2 border-white flex items-center justify-center text-white text-xs font-bold"
                    >
                      {i}
                    </div>
                  ))}
                </div>
                <span className="text-sm text-gray-600">
                  <strong>500+</strong> businesses trust us
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="text-yellow-400 flex gap-0.5">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <span key={i}>★</span>
                  ))}
                </div>
                <span className="text-sm text-gray-600">
                  <strong>4.9/5</strong> rating
                </span>
              </div>
            </div>
          </div>

          {/* Right Visual */}
          <div className="hidden lg:flex justify-center">
            <div className="relative w-full max-w-md">
              {/* Floating card with gradient */}
              <div className="bg-white rounded-2xl shadow-2xl overflow-hidden border border-gray-100">
                <div className="bg-gradient-to-r from-blue-600 to-blue-700 h-32 flex items-center justify-center">
                  <div className="text-center text-white">
                    <div className="text-4xl font-bold">+245%</div>
                    <div className="text-sm opacity-90">Campaign Growth</div>
                  </div>
                </div>
                <div className="p-6 space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Engagement Rate</span>
                      <span className="font-semibold text-green-600">+34%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-blue-600 to-blue-500 h-2 rounded-full"
                        style={{ width: "85%" }}
                      ></div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Conversion Rate</span>
                      <span className="font-semibold text-green-600">+18%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-blue-400 h-2 rounded-full"
                        style={{ width: "72%" }}
                      ></div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">ROI Improvement</span>
                      <span className="font-semibold text-green-600">+56%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-blue-400 to-blue-300 h-2 rounded-full"
                        style={{ width: "92%" }}
                      ></div>
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
