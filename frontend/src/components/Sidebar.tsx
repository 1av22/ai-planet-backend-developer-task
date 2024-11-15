"use client"

import { useState } from 'react'
import { Button } from './ui/button'
import { Upload } from 'lucide-react'
import { useModal } from '@/context/ModalContext'

type File = {
    id: number
    name: string
    size: string
    type: string
    date: Date
}

const Sidebar = () => {
    const [files] = useState<File[]>([
        { id: 1, name: "Document.pdf", size: "2.4 MB", type: "PDF", date: new Date() },
        { id: 2, name: "Image.jpg", size: "1.2 MB", type: "Image", date: new Date() },
        { id: 3, name: "Spreadsheet.xlsx", size: "3.1 MB", type: "Excel", date: new Date() }
    ])

    const { setShowUploadCard } = useModal()

    return (
        <div className="h-full w-full p-4 bg-background">
            <h2 className="text-xl font-bold mb-4">Files</h2>
            <div className="space-y-2">
                {files.map((file) => (
                    <div
                        key={file.id}
                        className="p-3 rounded-lg hover:bg-muted cursor-pointer transition-colors"
                    >
                        <div className="flex justify-between items-center">
                            <span className="font-medium">{file.name}</span>
                            <span className="text-sm text-muted-foreground">{file.size}</span>
                        </div>
                        <div className="flex justify-between items-center mt-1">
                            <span className="text-sm text-muted-foreground">{file.type}</span>
                            <span className="text-sm text-muted-foreground">
                                {file.date.toLocaleDateString()}
                            </span>
                        </div>
                    </div>
                ))}
            </div>

            <div className='my-5 w-full'>
                <Button
                    className='w-full'
                    onClick={() => setShowUploadCard(true)}
                >
                    <Upload className='w-4 h-4 mr-2' />
                    Upload New File
                </Button>
            </div>
        </div>
    )
}

export default Sidebar