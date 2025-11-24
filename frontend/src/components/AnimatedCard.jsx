import { motion } from 'framer-motion'

export default function AnimatedCard({ children, delay = 0, className = '' }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className={`glass ${className}`}
    >
      {children}
    </motion.div>
  )
}


