"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

export default function RootPage() {
    const router = useRouter();

    useEffect(() => {
        // Check if user is logged in
        const token = localStorage.getItem("auth_token");
        if (token) {
            router.push("/dashboard");
        } else {
            router.push("/landing");
        }
    }, [router]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
        </div>
    );
}
