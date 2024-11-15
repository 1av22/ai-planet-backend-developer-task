"use client"

import UploadCard from '@/components/UploadCard'
import { createContext, useContext, useState } from 'react'

type ModalContextType = {
    showUploadCard: boolean
    setShowUploadCard: (show: boolean) => void
}

const ModalContext = createContext<ModalContextType | undefined>(undefined)

export function ModalProvider({ children }: { children: React.ReactNode }) {
    const [showUploadCard, setShowUploadCard] = useState(false)

    return (
        <ModalContext.Provider value={{ showUploadCard, setShowUploadCard }}>
            {children}
            {showUploadCard && (
                <div
                    className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center"
                    onClick={() => setShowUploadCard(false)}
                >
                    <div
                        className="w-full max-w-md p-4 animate-in fade-in-0 zoom-in-95"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <UploadCard onClose={() => setShowUploadCard(false)} />
                    </div>
                </div>
            )}
        </ModalContext.Provider>
    )
}

export function useModal() {
    const context = useContext(ModalContext)
    if (context === undefined) {
        throw new Error('useModal must be used within a ModalProvider')
    }
    return context
} 