import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, Edit3, Save } from 'lucide-react'
import AnimatedCard from './AnimatedCard'
import FieldConfidenceBar from './FieldConfidenceBar'

export default function ExtractedForm({
  fields,
  fieldConfidences,
  documentConfidence,
  onFieldChange,
  onSubmit,
  onReset,
}) {
  const [editingField, setEditingField] = useState(null)
  const [formValues, setFormValues] = useState(fields)

  // Update formValues when fields prop changes
  useEffect(() => {
    if (fields) {
      setFormValues(fields)
      console.log('Form values updated:', fields)
    }
  }, [fields])

  const handleFieldChange = (fieldName, value) => {
    setFormValues({ ...formValues, [fieldName]: value })
    onFieldChange({ ...formValues, [fieldName]: value })
  }

  const handleSubmit = () => {
    onSubmit(formValues)
  }

  // Generate human-readable label for any field name
  const getFieldLabel = (fieldName) => {
    const labelMap = {
      name: 'Full Name',
      age: 'Age',
      gender: 'Gender',
      phone: 'Phone Number',
      email: 'Email Address',
      address: 'Address',
      address_line1: 'Address Line 1',
      address_line2: 'Address Line 2',
      city: 'City',
      state: 'State',
      country: 'Country',
      date_of_birth: 'Date of Birth',
      pin_code: 'PIN Code',
      aadhaar: 'Aadhaar Number',
      pan: 'PAN Number',
      passport: 'Passport Number',
      occupation: 'Occupation',
    }
    
    // If field name exists in map, use it; otherwise format the field name
    if (labelMap[fieldName]) {
      return labelMap[fieldName]
    }
    
    // Format unknown field names: date_of_birth -> Date of Birth
    return fieldName
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }
  
  // Get field type for input rendering
  const getFieldType = (fieldName) => {
    if (fieldName === 'email') return 'email'
    if (fieldName === 'age' || fieldName === 'pin_code') return 'number'
    return 'text'
  }
  
  // Check if field should be a textarea
  const isTextareaField = (fieldName) => {
    return fieldName === 'address' || fieldName === 'address_line1' || fieldName === 'address_line2'
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Confidence Summary */}
      <AnimatedCard className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-white">Extraction Confidence</h3>
          <motion.div
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-400/30"
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3 }}
          >
            <span className="text-2xl font-bold gradient-text">
              {Math.round(documentConfidence * 100)}%
            </span>
          </motion.div>
        </div>
        <div className="space-y-2">
          {Object.entries(fieldConfidences || {}).map(([field, conf]) => (
            <FieldConfidenceBar
              key={field}
              confidence={conf}
              fieldName={getFieldLabel(field)}
            />
          ))}
        </div>
      </AnimatedCard>

      {/* Form Fields */}
      <AnimatedCard delay={0.2} className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Extracted Information</h2>
          <p className="text-sm text-white/60">Review and edit as needed</p>
        </div>

        <div className="space-y-6">
          {Object.entries(formValues || {}).map(([fieldName, value], index) => {
            const label = getFieldLabel(fieldName)
            return (
              <motion.div
                key={fieldName}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 * index }}
                className="space-y-2"
              >
                <label className="block text-sm font-semibold text-white/90">
                  {label}
                </label>
                {isTextareaField(fieldName) ? (
                  <textarea
                    value={value || ''}
                    onChange={(e) => handleFieldChange(fieldName, e.target.value)}
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                    rows={3}
                    placeholder={`Enter ${label.toLowerCase()}`}
                  />
                ) : (
                  <input
                    type={getFieldType(fieldName)}
                    value={value || ''}
                    onChange={(e) => handleFieldChange(fieldName, e.target.value)}
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder={`Enter ${label.toLowerCase()}`}
                  />
                )}
                {fieldConfidences?.[fieldName] && (
                  <p className="text-xs text-white/50">
                    Confidence: {Math.round(fieldConfidences[fieldName] * 100)}%
                  </p>
                )}
              </motion.div>
            )
          })}
          {(!formValues || Object.keys(formValues).length === 0) && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-8 text-white/60"
            >
              <p>No fields were extracted from this document.</p>
              <p className="text-sm mt-2">Please check the raw text output or try a different image.</p>
            </motion.div>
          )}
        </div>

        <div className="mt-8 flex gap-4">
          <motion.button
            onClick={onReset}
            className="flex-1 px-6 py-3 bg-white/10 border border-white/20 text-white rounded-lg font-semibold hover:bg-white/20 transition"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Start Over
          </motion.button>
          <motion.button
            onClick={handleSubmit}
            className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-purple-500/50 transition flex items-center justify-center gap-2"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <CheckCircle className="w-5 h-5" />
            Verify Information
          </motion.button>
        </div>
      </AnimatedCard>
    </div>
  )
}


