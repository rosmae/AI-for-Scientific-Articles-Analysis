// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

// Ensure canvas-confetti is properly typed
declare module 'canvas-confetti' {
	interface ConfettiOptions {
		particleCount?: number;
		spread?: number;
		origin?: { x?: number; y?: number };
		colors?: string[];
		zIndex?: number;
		[key: string]: any;
	}
	
	function confetti(options?: ConfettiOptions): Promise<void>;
	export = confetti;
}

export {};
