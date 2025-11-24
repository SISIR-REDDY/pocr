import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'

export default function LoaderSpinner({ message = 'Loading...' }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-strong p-12 text-center"
    >
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        className="inline-block mb-6"
      >
        <Loader2 className="w-16 h-16 text-purple-400" />
      </motion.div>
      <p className="text-white text-lg font-semibold">{message}</p>
      <motion.div
        className="mt-4 h-1 bg-white/10 rounded-full overflow-hidden max-w-xs mx-auto"
        initial={{ width: 0 }}
        animate={{ width: '100%' }}
        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
      >
        <motion.div
          className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
          animate={{ x: ['-100%', '100%'] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
        />
      </motion.div>
    </motion.div>
  )
}


