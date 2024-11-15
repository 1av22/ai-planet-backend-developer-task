"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import Image from "next/image"
import { useRouter } from "next/navigation"

export default function SignIn() {

  const router = useRouter()
  return (
    <div className="flex max-w-screen-xl mx-auto px-4 min-h-screen">
      {/* Left side - Image */}
      <div className="hidden lg:flex lg:w-1/2 lg:items-center lg:justify-center">
        <Image
          src="/Hero.png"
          alt="Sign In"
          width={500}
          height={500}
          className="scale-x-[-1]"
        />
      </div>

      {/* Right side - Sign In Form */}
      <div className="flex w-full items-center justify-center lg:w-1/2">
        <Card className="w-[350px]">
          <CardHeader>
            <CardTitle className="text-2xl">Sign In</CardTitle>
          </CardHeader>
          <CardContent>
            <form>
              <div className="grid w-full items-center gap-4">
                <div className="flex flex-col space-y-1.5">
                  <Label htmlFor="email">Email or Username</Label>
                  <Input id="email" placeholder="Enter your email or username" />
                </div>
                <div className="flex flex-col space-y-1.5">
                  <Label htmlFor="password">Password</Label>
                  <Input id="password" type="password" placeholder="Enter your password" />
                </div>
              </div>
            </form>
          </CardContent>
          <CardFooter className="flex flex-col space-y-2 w-full">
            <Button className="w-full">Sign In</Button>
            <Button 
            variant="ghost" 
            className="w-full hover:bg-transparent"
            onClick={() => router.push('/sign-up')}
            >Create an account</Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}