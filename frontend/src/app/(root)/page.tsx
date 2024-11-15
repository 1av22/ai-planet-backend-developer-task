import { Hero } from "@/components";
import Image from "next/image";

export default function Home() {
  return (
    <div className="max-w-screen-xl mx-auto px-4 h-screen flex justify-center items-center">
      <Hero />
    </div>
  );
}
