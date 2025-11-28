import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Navbar from './components/Navbar'
import UploadBox from './components/UploadBox'
import ExtractedForm from './components/ExtractedForm'
import VerificationPanel from './components/VerificationPanel'
import LoaderSpinner from './components/LoaderSpinner'
import { API_VERIFY_URL } from './config'

function App() {
  const [step, setStep] = useState('upload') // upload, extracting, form, verifying, results
  const [extractionData, setExtractionData] = useState(null)
  const [formData, setFormData] = useState({})
  const [verificationResult, setVerificationResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleExtractionComplete = (data) => {
    console.log('Extraction complete, received data:', data)
    setExtractionData(data)
    // Ensure we get fields from the correct location in response
    const extractedFields = data.fields || {}
    console.log('Setting form data:', extractedFields)
    setFormData(extractedFields)
    setStep('form')
  }

  const handleFormSubmit = async (submittedFields) => {
    if (!extractionData || !extractionData.fields) {
      alert('No extraction data available. Please extract again.')
      return
    }
    
    setLoading(true)
    setStep('verifying')
    
    try {
      // Clean submitted fields - convert None/empty to empty strings
      const cleanedSubmittedFields = {}
      for (const [key, value] of Object.entries(submittedFields)) {
        cleanedSubmittedFields[key] = value || ''
      }
      
      // Clean extracted fields - convert None to empty strings
      const cleanedExtractedFields = {}
      for (const [key, value] of Object.entries(extractionData.fields || {})) {
        cleanedExtractedFields[key] = value || ''
      }
      
      console.log('Sending verification request:', {
        submitted_fields: cleanedSubmittedFields,
        extracted_fields: cleanedExtractedFields
      })
      
      const response = await fetch(API_VERIFY_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          submitted_fields: cleanedSubmittedFields,
          extracted_fields: cleanedExtractedFields,
        }),
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Verification error response:', errorText)
        throw new Error(`Verification failed: ${response.statusText} - ${errorText}`)
      }
      
      const result = await response.json()
      setVerificationResult(result)
      setStep('results')
    } catch (error) {
      console.error('Verification error:', error)
      alert('Verification failed. Please try again.')
      setStep('form')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setStep('upload')
    setExtractionData(null)
    setFormData({})
    setVerificationResult(null)
  }

  return (
    <div className="min-h-screen">
      <Navbar />
      
      <main className="container mx-auto px-4 py-8">
        <AnimatePresence mode="wait">
          {step === 'upload' && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <UploadBox
                onExtractionStart={() => {
                  setStep('extracting')
                  setLoading(true)
                }}
                onExtractionComplete={handleExtractionComplete}
                onError={() => {
                  setStep('upload')
                  setLoading(false)
                }}
              />
            </motion.div>
          )}

          {step === 'extracting' && (
            <motion.div
              key="extracting"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center justify-center min-h-[60vh]"
            >
              <LoaderSpinner message="Extracting text from document..." />
            </motion.div>
          )}

          {step === 'form' && extractionData && (
            <motion.div
              key="form"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
            >
              <ExtractedForm
                fields={formData}
                fieldConfidences={extractionData.field_confidences || {}}
                documentConfidence={extractionData.confidence || 0}
                onFieldChange={setFormData}
                onSubmit={handleFormSubmit}
                onReset={handleReset}
              />
            </motion.div>
          )}

          {step === 'verifying' && (
            <motion.div
              key="verifying"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center justify-center min-h-[60vh]"
            >
              <LoaderSpinner message="Verifying information..." />
            </motion.div>
          )}

          {step === 'results' && verificationResult && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <VerificationPanel
                result={verificationResult}
                onReset={handleReset}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}

export default App


