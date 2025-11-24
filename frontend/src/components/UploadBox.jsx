import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { Upload, FileText, Image as ImageIcon, X } from 'lucide-react'
import axios from 'axios'

export default function UploadBox({ onExtractionStart, onExtractionComplete, onError }) {
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleSubmit = async () => {
    if (!selectedFile) {
      alert('Please select a file to upload')
      return
    }

    onExtractionStart()

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await axios.post('http://localhost:8000/api/extract', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      // Check if extraction was successful
      if (response.data.success === false) {
        throw new Error(response.data.error || 'Extraction failed')
      }

      onExtractionComplete(response.data)
    } catch (error) {
      console.error('Extraction error:', error)
      alert('Extraction failed. Please try again.')
      onError()
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-strong p-8"
      >
        <h2 className="text-3xl font-bold text-white mb-2 text-center">
          Upload Document
        </h2>
        <p className="text-white/70 text-center mb-8">
          Upload an image or PDF to extract information
        </p>

        <motion.div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`
            relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer
            transition-all duration-300
            ${isDragging ? 'border-purple-400 bg-purple-500/20' : 'border-white/30 bg-white/5'}
            ${selectedFile ? 'border-green-400 bg-green-500/10' : ''}
          `}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*,.pdf"
            onChange={handleFileSelect}
            className="hidden"
          />

          {selectedFile ? (
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="space-y-4"
            >
              {selectedFile.type.startsWith('image/') ? (
                <ImageIcon className="w-16 h-16 mx-auto text-green-400" />
              ) : (
                <FileText className="w-16 h-16 mx-auto text-green-400" />
              )}
              <div>
                <p className="text-white font-semibold">{selectedFile.name}</p>
                <p className="text-white/60 text-sm">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setSelectedFile(null)
                }}
                className="mt-4 px-4 py-2 bg-red-500/20 text-red-300 rounded-lg hover:bg-red-500/30 transition"
              >
                <X className="w-4 h-4 inline mr-2" />
                Remove
              </button>
            </motion.div>
          ) : (
            <>
              <Upload className="w-16 h-16 mx-auto text-white/50 mb-4" />
              <p className="text-white text-lg mb-2">
                Drag & drop your file here
              </p>
              <p className="text-white/60">or click to browse</p>
              <p className="text-white/40 text-sm mt-4">
                Supports: PNG, JPG, JPEG, PDF
              </p>
            </>
          )}
        </motion.div>

        <div className="mt-6">
          <motion.button
            onClick={handleSubmit}
            disabled={!selectedFile}
            className="w-full px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition"
            whileHover={{ scale: selectedFile ? 1.02 : 1 }}
            whileTap={{ scale: selectedFile ? 0.98 : 1 }}
          >
            Extract Information
          </motion.button>
        </div>
      </motion.div>
    </div>
  )
}


