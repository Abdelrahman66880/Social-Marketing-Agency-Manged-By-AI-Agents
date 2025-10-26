import Link from "next/link"
import { Zap } from "lucide-react"

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-white">AI Agent</span>
            </div>
            <p className="text-sm text-gray-400">Automate your Facebook marketing with intelligent AI assistance.</p>
          </div>

          {/* Product */}
          <div className="space-y-4">
            <h3 className="font-semibold text-white">Product</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/dashboard" className="hover:text-blue-400 transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/generate" className="hover:text-blue-400 transition-colors">
                  Content Generator
                </Link>
              </li>
              <li>
                <Link href="/competitors" className="hover:text-blue-400 transition-colors">
                  Competitor Insights
                </Link>
              </li>
              <li>
                <Link href="/messages" className="hover:text-blue-400 transition-colors">
                  Messenger Replies
                </Link>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div className="space-y-4">
            <h3 className="font-semibold text-white">Company</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="#" className="hover:text-blue-400 transition-colors">
                  About Us
                </Link>
              </li>
              <li>
                <Link href="#" className="hover:text-blue-400 transition-colors">
                  Blog
                </Link>
              </li>
              <li>
                <Link href="#" className="hover:text-blue-400 transition-colors">
                  Careers
                </Link>
              </li>
              <li>
                <Link href="#" className="hover:text-blue-400 transition-colors">
                  Contact
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div className="space-y-4">
            <h3 className="font-semibold text-white">Legal</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="#" className="hover:text-blue-400 transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="#" className="hover:text-blue-400 transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="#" className="hover:text-blue-400 transition-colors">
                  Cookie Policy
                </Link>
              </li>
              <li>
                <Link href="#" className="hover:text-blue-400 transition-colors">
                  Support
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-gray-800 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-400">© 2025 AI Agent for Social Media Marketing. All rights reserved.</p>
            <p className="text-sm text-gray-400">Powered by FastAPI + Hugging Face LLM + Meta Graph API</p>
          </div>
        </div>
      </div>
    </footer>
  )
}
