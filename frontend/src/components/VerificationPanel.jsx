import { motion } from 'framer-motion'
import { CheckCircle, XCircle, AlertCircle, RotateCcw } from 'lucide-react'
import AnimatedCard from './AnimatedCard'

export default function VerificationPanel({ result, onReset }) {
  const { matches, mismatches, overall_score, verification_passed } = result

  const fieldLabels = {
    name: 'Full Name',
    age: 'Age',
    gender: 'Gender',
    phone: 'Phone Number',
    email: 'Email Address',
    address: 'Address',
  }

  const getMatchColor = (score) => {
    if (score >= 0.9) return 'text-green-400'
    if (score >= 0.7) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getMatchIcon = (score) => {
    if (score >= 0.9) return <CheckCircle className="w-5 h-5 text-green-400" />
    if (score >= 0.7) return <AlertCircle className="w-5 h-5 text-yellow-400" />
    return <XCircle className="w-5 h-5 text-red-400" />
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Overall Result */}
      <AnimatedCard className="p-8">
        <div className="text-center">
          {verification_passed ? (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200 }}
            >
              <CheckCircle className="w-20 h-20 text-green-400 mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-green-400 mb-2">
                Verification Passed!
              </h2>
              <p className="text-white/70">
                All information matches the extracted data
              </p>
            </motion.div>
          ) : (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200 }}
            >
              <XCircle className="w-20 h-20 text-red-400 mx-auto mb-4" />
              <h2 className="text-3xl font-bold text-red-400 mb-2">
                Verification Issues Found
              </h2>
              <p className="text-white/70">
                Some fields don't match the extracted data
              </p>
            </motion.div>
          )}
          
          <motion.div
            className="mt-6 inline-block px-6 py-3 bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-400/30 rounded-lg"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <span className="text-3xl font-bold gradient-text">
              {Math.round(overall_score * 100)}%
            </span>
            <p className="text-sm text-white/60 mt-1">Overall Match Score</p>
          </motion.div>
        </div>
      </AnimatedCard>

      {/* Field-by-Field Results */}
      <AnimatedCard delay={0.2} className="p-6">
        <h3 className="text-xl font-bold text-white mb-6">Field Verification</h3>
        <div className="space-y-4">
          {Object.entries(matches || {}).map(([field, score], index) => (
            <motion.div
              key={field}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index }}
              className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10"
            >
              <div className="flex items-center gap-3">
                {getMatchIcon(score)}
                <span className="text-white font-medium">
                  {fieldLabels[field] || field}
                </span>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-32 h-2 bg-white/10 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${score * 100}%` }}
                    transition={{ delay: 0.2 + 0.1 * index, duration: 0.5 }}
                    className={`h-full ${
                      score >= 0.9 ? 'bg-green-500' :
                      score >= 0.7 ? 'bg-yellow-500' :
                      'bg-red-500'
                    } rounded-full`}
                  />
                </div>
                <span className={`font-semibold ${getMatchColor(score)}`}>
                  {Math.round(score * 100)}%
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </AnimatedCard>

      {/* Mismatches Detail */}
      {mismatches && mismatches.length > 0 && (
        <AnimatedCard delay={0.4} className="p-6 border-red-500/30">
          <h3 className="text-xl font-bold text-red-400 mb-4 flex items-center gap-2">
            <AlertCircle className="w-6 h-6" />
            Mismatched Fields
          </h3>
          <div className="space-y-4">
            {mismatches.map((mismatch, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + 0.1 * index }}
                className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg"
              >
                <p className="font-semibold text-white mb-2">
                  {fieldLabels[mismatch.field] || mismatch.field}
                </p>
                <div className="space-y-1 text-sm">
                  <p className="text-white/70">
                    <span className="text-green-400">Submitted:</span> {mismatch.submitted || 'N/A'}
                  </p>
                  <p className="text-white/70">
                    <span className="text-yellow-400">Extracted:</span> {mismatch.extracted || 'N/A'}
                  </p>
                  <p className="text-red-400 text-xs mt-2">
                    Match: {Math.round(mismatch.match_score * 100)}%
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </AnimatedCard>
      )}

      {/* Reset Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="text-center"
      >
        <motion.button
          onClick={onReset}
          className="px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-purple-500/50 transition flex items-center gap-2 mx-auto"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <RotateCcw className="w-5 h-5" />
          Start New Extraction
        </motion.button>
      </motion.div>
    </div>
  )
}


