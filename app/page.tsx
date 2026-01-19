"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useAppSelector } from "./lib/hooks";

export default function RootPage() {
    const router = useRouter();
    const { isAuthenticated, isLoading } = useAppSelector((state) => state.auth);

    useEffect(() => {
        if (!isLoading) {
            if (isAuthenticated) {
                router.push("/dashboard");
            } else {
                router.push("/landing");
            }
        }
    }, [isAuthenticated, isLoading, router]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
        </div>
    );
}
