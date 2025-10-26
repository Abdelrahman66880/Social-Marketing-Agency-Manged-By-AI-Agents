import { Star } from "lucide-react"

export default function TestimonialsSection() {
  const testimonials = [
    {
      name: "Jane D.",
      business: "Local Cafe Owner",
      quote: "The AI Agent saved me hours every week! My Facebook engagement has never been better.",
      rating: 5,
      avatar: "JD",
    },
    {
      name: "Marcus T.",
      business: "E-commerce Store",
      quote: "Incredible ROI improvement. The automated posts are converting like crazy. Highly recommend!",
      rating: 5,
      avatar: "MT",
    },
    {
      name: "Sarah L.",
      business: "Beauty Salon",
      quote: "Finally, a tool that understands my business. The competitor insights are game-changing.",
      rating: 5,
      avatar: "SL",
    },
  ]

  return (
    <section className="py-20 sm:py-32 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 text-balance">Loved by Businesses</h2>
          <p className="text-xl text-gray-600">See what our customers have to say about AI Agent</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              className="bg-gradient-to-br from-blue-50 to-white rounded-xl p-8 border border-blue-100 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex gap-1 mb-4">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                ))}
              </div>

              <p className="text-gray-700 mb-6 leading-relaxed italic">"{testimonial.quote}"</p>

              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-full flex items-center justify-center text-white font-bold text-sm">
                  {testimonial.avatar}
                </div>
                <div>
                  <div className="font-semibold text-gray-900">{testimonial.name}</div>
                  <div className="text-sm text-gray-600">{testimonial.business}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
