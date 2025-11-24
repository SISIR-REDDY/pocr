import { motion } from 'framer-motion'

export default function FieldConfidenceBar({ confidence, fieldName }) {
  const percentage = Math.round(confidence * 100)
  const colorClass = 
    confidence >= 0.8 ? 'bg-green-500' :
    confidence >= 0.6 ? 'bg-yellow-500' :
    'bg-red-500'

  return (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-1">
        <span className="text-sm text-white/70 capitalize">{fieldName}</span>
        <span className="text-sm font-semibold text-white">{percentage}%</span>
      </div>
      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className={`h-full ${colorClass} rounded-full`}
        />
      </div>
    </div>
  )
}


