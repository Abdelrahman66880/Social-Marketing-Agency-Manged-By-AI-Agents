import { Brain, TrendingUp, Eye, MessageCircle, Zap } from "lucide-react"

export default function FeaturesSection() {
  const features = [
    {
      icon: Brain,
      title: "AI Post Generation",
      description: "Create custom marketing posts using large language models tailored to your audience.",
    },
    {
      icon: TrendingUp,
      title: "Customer Insights",
      description: "Analyze comments and messages for engagement and sentiment in real-time.",
    },
    {
      icon: Eye,
      title: "Competitor Monitoring",
      description: "Track top-performing pages in your industry and stay ahead of competition.",
    },
    {
      icon: MessageCircle,
      title: "Auto Replies",
      description: "Respond instantly to customers via Messenger with AI-powered responses.",
    },
    {
      icon: Zap,
      title: "Offer Recommendations",
      description: "Get AI suggestions for promotions and ad boosts based on market trends.",
    },
  ]

  return (
    <section className="py-20 sm:py-32 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 text-balance">
            Everything You Need to Market Smarter
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Powerful features designed to help small business owners succeed on Facebook
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <div
                key={index}
                className="bg-white rounded-xl p-6 shadow-sm hover:shadow-lg transition-shadow duration-300 border border-gray-100 hover:border-blue-200"
              >
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600 text-sm leading-relaxed">{feature.description}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
