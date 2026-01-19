'use client';

import { useRef } from 'react';
import { Provider } from 'react-redux';
import { makeStore, AppStore } from './lib/store';
import { checkAuth } from './lib/features/auth/authSlice';

export default function StoreProvider({
    children,
}: {
    children: React.ReactNode;
}) {
    const storeRef = useRef<AppStore>(undefined);
    if (!storeRef.current) {
        // Create the store instance the first time this renders
        storeRef.current = makeStore();
        // Check initial auth state
        storeRef.current.dispatch(checkAuth());
    }

    return <Provider store={storeRef.current}>{children}</Provider>;
}
