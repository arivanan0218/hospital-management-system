import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import ImageGallery from 'react-image-gallery';
import * as pdfjsLib from 'pdfjs-dist';
import { Upload, FileText, Image, AlertCircle, CheckCircle, Clock, Eye, X } from 'lucide-react';
import 'react-image-gallery/styles/css/image-gallery.css';

// Set up PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

const EnhancedMedicalDocumentUpload = ({ patientId, onUploadComplete }) => {
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [documentType, setDocumentType] = useState('prescription');
  const [previewFile, setPreviewFile] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [pdfPages, setPdfPages] = useState(null);

  const documentTypes = [
    { value: 'prescription', label: 'Prescription' },
    { value: 'lab_result', label: 'Lab Result' },
    { value: 'imaging', label: 'Medical Imaging' },
    { value: 'discharge_summary', label: 'Discharge Summary' },
    { value: 'consultation_note', label: 'Consultation Note' },
    { value: 'insurance_document', label: 'Insurance Document' },
    { value: 'other', label: 'Other' }
  ];

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      setUploadStatus({
        type: 'error',
        message: 'Some files were rejected. Please check file types and sizes.'
      });
    }

    if (acceptedFiles.length > 0) {
      const newFiles = acceptedFiles.map(file => ({
        file,
        id: Math.random().toString(36).substr(2, 9),
        preview: URL.createObjectURL(file),
        type: file.type,
        size: file.size,
        name: file.name
      }));
      
      setSelectedFiles(prev => [...prev, ...newFiles]);
      setUploadStatus(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif'],
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true
  });

  const removeFile = (fileId) => {
    setSelectedFiles(prev => {
      const updated = prev.filter(f => f.id !== fileId);
      // Revoke object URL to prevent memory leaks
      const fileToRemove = prev.find(f => f.id === fileId);
      if (fileToRemove?.preview) {
        URL.revokeObjectURL(fileToRemove.preview);
      }
      return updated;
    });
  };

  const previewDocument = (fileData) => {
    setPreviewFile(fileData);
    setShowPreview(true);
    
    if (fileData.type === 'application/pdf') {
      // Load PDF for preview
      loadPDF(fileData.file);
    }
  };

  const loadPDF = async (file) => {
    try {
      const fileURL = URL.createObjectURL(file);
      const pdf = await pdfjsLib.getDocument(fileURL).promise;
      setPdfPages(pdf.numPages);
    } catch (error) {
      console.error('Error loading PDF:', error);
    }
  };

  const convertFileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  };

  const uploadDocuments = async () => {
    if (selectedFiles.length === 0 || !patientId) {
      setUploadStatus({
        type: 'error',
        message: 'Please select files and ensure patient ID is available.'
      });
      return;
    }

    setUploading(true);
    setUploadStatus(null);

    try {
      const uploadResults = [];
      
      for (const fileData of selectedFiles) {
        // Convert file to base64
        const base64Content = await convertFileToBase64(fileData.file);

        // Call the MCP upload tool
        const uploadResponse = await fetch('http://localhost:8000/tools/call', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            params: {
              name: 'upload_medical_document',
              arguments: {
                patient_id: patientId,
                document_type: documentType,
                file_content: base64Content,
                file_name: fileData.file.name,
                mime_type: fileData.file.type
              }
            }
          })
        });

        const uploadResult = await uploadResponse.json();
        
        if (uploadResult.result?.content?.[0]?.text) {
          const data = JSON.parse(uploadResult.result.content[0].text);
          
          if (data.success && data.result?.success) {
            const documentId = data.result.document_id;
            
            // Now process the document
            setProcessing(true);
            const processResponse = await fetch('http://localhost:8000/tools/call', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                params: {
                  name: 'process_medical_document',
                  arguments: {
                    document_id: documentId
                  }
                }
              })
            });

            const processResult = await processResponse.json();
            
            if (processResult.result?.content?.[0]?.text) {
              const processData = JSON.parse(processResult.result.content[0].text);
              
              if (processData.success && processData.result?.success) {
                uploadResults.push({
                  fileName: fileData.file.name,
                  documentId: documentId,
                  entitiesCount: processData.result.entities_count,
                  confidence: processData.result.confidence_score
                });
              }
            }
          }
        }
      }

      if (uploadResults.length > 0) {
        setUploadStatus({
          type: 'success',
          message: `Successfully uploaded and processed ${uploadResults.length} document(s)!`,
          results: uploadResults
        });

        // Call parent callback
        if (onUploadComplete) {
          onUploadComplete(uploadResults);
        }

        // Clear selected files
        setSelectedFiles([]);
      }

    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus({
        type: 'error',
        message: `Upload failed: ${error.message}`
      });
    } finally {
      setUploading(false);
      setProcessing(false);
    }
  };

  const renderPreview = () => {
    if (!showPreview || !previewFile) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 max-w-4xl max-h-[90vh] overflow-auto">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Preview: {previewFile.name}</h3>
            <button
              onClick={() => setShowPreview(false)}
              className="p-2 hover:bg-gray-100 rounded-full"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="preview-content">
            {previewFile.type.startsWith('image/') && (
              <img
                src={previewFile.preview}
                alt="Preview"
                className="max-w-full max-h-96 object-contain mx-auto"
              />
            )}

            {previewFile.type === 'application/pdf' && (
              <div className="pdf-preview">
                <div className="text-center">
                  <p className="text-gray-600 mb-4">
                    PDF Preview: {pdfPages} page(s)
                  </p>
                  <iframe
                    src={previewFile.preview}
                    width="100%"
                    height="500px"
                    className="border rounded"
                    title="PDF Preview"
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold mb-4 flex items-center">
        <Upload className="w-5 h-5 mr-2" />
        Upload Medical Documents
      </h3>

      {/* Document Type Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Document Type
        </label>
        <select
          value={documentType}
          onChange={(e) => setDocumentType(e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {documentTypes.map(type => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
      </div>

      {/* Enhanced Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        {isDragActive ? (
          <p className="text-blue-600">Drop the files here...</p>
        ) : (
          <div>
            <p className="text-lg mb-2">Drag & drop medical documents here</p>
            <p className="text-gray-500 mb-2">or click to browse</p>
            <p className="text-sm text-gray-400">
              Supports: Images (JPG, PNG, GIF), PDF, Text files (Max 10MB each)
            </p>
          </div>
        )}
      </div>

      {/* Selected Files Preview */}
      {selectedFiles.length > 0 && (
        <div className="mt-6">
          <h4 className="font-medium mb-3">Selected Files ({selectedFiles.length})</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {selectedFiles.map((fileData) => (
              <div key={fileData.id} className="border rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    {fileData.type.startsWith('image/') ? (
                      <Image className="w-5 h-5 mr-2 text-green-600" />
                    ) : (
                      <FileText className="w-5 h-5 mr-2 text-blue-600" />
                    )}
                    <span className="text-sm font-medium truncate">
                      {fileData.name}
                    </span>
                  </div>
                  <button
                    onClick={() => removeFile(fileData.id)}
                    className="p-1 hover:bg-gray-100 rounded"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">
                    {(fileData.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                  <button
                    onClick={() => previewDocument(fileData)}
                    className="flex items-center text-sm text-blue-600 hover:text-blue-800"
                  >
                    <Eye className="w-4 h-4 mr-1" />
                    Preview
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Button */}
      {selectedFiles.length > 0 && (
        <div className="mt-6">
          <button
            onClick={uploadDocuments}
            disabled={uploading || processing}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {uploading || processing ? (
              <>
                <Clock className="w-5 h-5 mr-2 animate-spin" />
                {uploading ? 'Uploading...' : 'Processing...'}
              </>
            ) : (
              <>
                <Upload className="w-5 h-5 mr-2" />
                Upload & Process Documents
              </>
            )}
          </button>
        </div>
      )}

      {/* Status Messages */}
      {uploadStatus && (
        <div className={`mt-4 p-4 rounded-lg ${
          uploadStatus.type === 'success' 
            ? 'bg-green-50 border border-green-200' 
            : 'bg-red-50 border border-red-200'
        }`}>
          <div className="flex items-center">
            {uploadStatus.type === 'success' ? (
              <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
            )}
            <span className={`font-medium ${
              uploadStatus.type === 'success' ? 'text-green-800' : 'text-red-800'
            }`}>
              {uploadStatus.message}
            </span>
          </div>
          
          {uploadStatus.results && (
            <div className="mt-2">
              {uploadStatus.results.map((result, index) => (
                <div key={index} className="text-sm text-green-700">
                  • {result.fileName}: {result.entitiesCount} entities extracted 
                  (confidence: {(result.confidence * 100).toFixed(1)}%)
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Preview Modal */}
      {renderPreview()}
    </div>
  );
};

export default EnhancedMedicalDocumentUpload;
