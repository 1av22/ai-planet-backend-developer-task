'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Send, Mic, PaperclipIcon, Menu } from 'lucide-react'
import { Sidebar, UploadCard } from '@/components'

type Message = {
    id: number
    text: string
    sender: 'user' | 'bot'
    timestamp: Date
}

export default function Component() {
    const [messages, setMessages] = useState<Message[]>([
        { id: 1, text: "Hello! How can I assist you today?", sender: 'bot', timestamp: new Date() }
    ])
    const [input, setInput] = useState('')
    const [isSidebarOpen, setIsSidebarOpen] = useState(false)
    const [showUploadCard, setShowUploadCard] = useState(false)

    const handleSend = () => {
        if (input.trim()) {
            const newMessage: Message = { id: messages.length + 1, text: input, sender: 'user', timestamp: new Date() }
            setMessages([...messages, newMessage])
            setInput('')

            // Simulate bot response
            setTimeout(() => {
                const botResponse: Message = {
                    id: messages.length + 2,
                    text: "I'm a simple bot. I don't have real responses yet, but I'm here to help!",
                    sender: 'bot',
                    timestamp: new Date()
                }
                setMessages(prevMessages => [...prevMessages, botResponse])
            }, 1000)
        }
    }

    return (
        <div className="flex h-screen bg-background">
            <div 
                className={`fixed inset-y-0 left-0 transform ${
                    isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
                } md:relative md:translate-x-0 transition-transform duration-200 ease-in-out z-30
                w-[280px] bg-background border-r`}
            >
                <Sidebar />
            </div>

            {isSidebarOpen && (
                <div 
                    className="fixed inset-0 bg-black/50 z-20 md:hidden"
                    onClick={() => setIsSidebarOpen(false)}
                />
            )}

            <div className="flex-1 flex flex-col w-full md:w-[calc(100%-280px)] relative">
                <header className="p-4 border-b flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <Button 
                            variant="ghost" 
                            size="icon" 
                            className="md:hidden"
                            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                        >
                            <Menu className="h-5 w-5" />
                            <span className="sr-only">Toggle files</span>
                        </Button>
                        <h1 className="text-2xl font-bold">ChatBot</h1>
                    </div>
                    <Button variant="outline" className="hidden sm:inline-flex">End Chat</Button>
                </header>

                <ScrollArea className="flex-grow p-4">
                    {messages.map((message) => (
                        <div
                            key={message.id}
                            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
                        >
                            <div className={`flex items-end max-w-[70%] ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                <Avatar className="w-10 h-10">
                                    <AvatarFallback>{message.sender === 'user' ? 'U' : 'B'}</AvatarFallback>
                                </Avatar>
                                <div className="flex flex-col mx-2">
                                    <div
                                        className={`py-2 px-3 rounded-lg ${message.sender === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}
                                    >
                                        {message.text}
                                    </div>
                                    <span className="text-xs text-muted-foreground mt-1">
                                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </ScrollArea>

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

                <div className="p-2 sm:p-4 border-t">
                    <form
                        onSubmit={(e) => {
                            e.preventDefault()
                            handleSend()
                        }}
                        className="flex items-center space-x-2"
                    >
                        <Button 
                            type="button" 
                            size="icon" 
                            variant="outline" 
                            className="hidden sm:inline-flex"
                            onClick={() => setShowUploadCard(!showUploadCard)}
                        >
                            <PaperclipIcon className="h-4 w-4" />
                            <span className="sr-only">Attach file</span>
                        </Button>
                        <Input
                            type="text"
                            placeholder="Type your message..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            className="flex-grow"
                        />
                        <Button type="button" size="icon" variant="outline" className="hidden sm:inline-flex">
                            <Mic className="h-4 w-4" />
                            <span className="sr-only">Voice input</span>
                        </Button>
                        <Button type="submit" size="icon">
                            <Send className="h-4 w-4" />
                            <span className="sr-only">Send</span>
                        </Button>
                    </form>
                </div>
            </div>

        </div>
    )
}