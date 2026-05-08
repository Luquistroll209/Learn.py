// src/lib/stores/rateLimitStore.ts
import { writable } from "svelte/store";

export interface RateLimitState {
  visible: boolean;
  message: string;
  remainingSeconds: number;
}

function createRateLimitStore() {
  const { subscribe, set, update } = writable<RateLimitState>({
    visible: false,
    message: "",
    remainingSeconds: 0,
  });

  let countdownInterval: number | null = null;

  function show(message: string, waitSeconds: number = 0) {
    if (countdownInterval) {
      clearInterval(countdownInterval);
      countdownInterval = null;
    }

    set({
      visible: true,
      message: message,
      remainingSeconds: waitSeconds,
    });

    if (waitSeconds > 0) {
      countdownInterval = setInterval(() => {
        update((state) => {
          if (state.remainingSeconds <= 1) {
            if (countdownInterval) clearInterval(countdownInterval);
            countdownInterval = null;
            return { ...state, remainingSeconds: 0 };
          }
          return { ...state, remainingSeconds: state.remainingSeconds - 1 };
        });
      }, 1000);
    }
  }

  function hide() {
    if (countdownInterval) {
      clearInterval(countdownInterval);
      countdownInterval = null;
    }
    set({ visible: false, message: "", remainingSeconds: 0 });
  }

  return {
    subscribe,
    show,
    hide,
  };
}

export const rateLimitStore = createRateLimitStore();
