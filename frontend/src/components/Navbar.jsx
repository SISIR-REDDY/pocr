import { motion } from 'framer-motion'
import { FileText } from 'lucide-react'

export default function Navbar() {
  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="glass-strong sticky top-0 z-50"
    >
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <motion.div
            className="flex items-center space-x-3"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold gradient-text">MOSIP OCR</h1>
              <p className="text-xs text-white/70">Text Extraction & Verification</p>
            </div>
          </motion.div>
          
          <motion.div
            className="px-4 py-2 bg-white/10 rounded-lg border border-white/20"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <span className="text-sm text-white/90">Local TrOCR Engine</span>
          </motion.div>
        </div>
      </div>
    </motion.nav>
  )
}


