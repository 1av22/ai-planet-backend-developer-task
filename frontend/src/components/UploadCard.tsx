'use client'

import { useState, useCallback } from 'react'
import { Upload, File, X } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

interface UploadCardProps {
    onClose?: () => void;
}

const UploadCard = ({ onClose }: UploadCardProps) => {
    const [file, setFile] = useState<File | null>(null)
    const [error, setError] = useState<string | null>(null)

    const onDrop = useCallback((acceptedFiles: File[]) => {
        handleFiles(acceptedFiles)
    }, [])

    const handleFiles = (files: FileList | File[]) => {
        const selectedFile = files[0]
        if (selectedFile) {
            if (selectedFile.type.startsWith('image/') || selectedFile.type === 'application/pdf') {
                setFile(selectedFile)
                setError(null)
            } else {
                setError('Please upload an image or PDF file.')
                setFile(null)
            }
        }
    }

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault()
        e.stopPropagation()
    }

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault()
        e.stopPropagation()
        const { files } = e.dataTransfer
        handleFiles(files)
    }

    const removeFile = () => {
        setFile(null)
        setError(null)
    }

    return (
        <Card className="w-full shadow-lg relative bg-card">
            <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Upload File</CardTitle>
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={onClose}
                    className="h-8 w-8 rounded-full"
                >
                    <X className="h-4 w-4" />
                    <span className="sr-only">Close</span>
                </Button>
            </CardHeader>
            <CardContent>
                <div
                    className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer"
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                >
                    <input
                        id="file-upload"
                        type="file"
                        className="sr-only"
                        onChange={(e) => handleFiles(e.target.files as FileList)}
                        accept="image/*,application/pdf"
                    />
                    <label
                        htmlFor="file-upload"
                        className="w-full flex flex-col items-center justify-center cursor-pointer text-center"
                    >
                        <Upload className="w-8 h-8 text-gray-400" />
                        <p className="mt-2 text-sm text-gray-500 text-center">
                            Drag and drop your file here, or click to select
                        </p>
                        <Button variant="outline" size="sm" className="mt-4">
                            Select File
                        </Button>
                    </label>
                </div>
                {error && <p className="mt-2 text-sm text-red-500 text-center w-full">{error}</p>}
                {file && (
                    <div className="mt-4 flex items-center justify-between bg-gray-100 p-2 rounded w-full">
                        <div className="flex items-center justify-center flex-1">
                            <File className="w-4 h-4 mr-2 text-gray-500" />
                            <span className="text-sm text-gray-700 truncate max-w-[200px] text-center">
                                {file.name}
                            </span>
                        </div>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={removeFile}
                            className="text-gray-500 hover:text-gray-700"
                        >
                            <X className="w-4 h-4" />
                            <span className="sr-only">Remove file</span>
                        </Button>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}

export default UploadCard
