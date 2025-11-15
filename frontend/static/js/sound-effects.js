// Efectos de sonido profesionales para FocusIT
class SoundEffects {
    constructor() {
        this.audioContext = null;
        this.enabled = true;
        this.volume = 0.5;
        this.init();
    }
    
    init() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (error) {
            console.log('Audio no disponible:', error);
            this.enabled = false;
        }
    }
    
    // Sonido para tickets críticos - Secuencia de alarma
    playCriticalAlert() {
        if (!this.enabled) return;
        
        const frequencies = [880, 1108, 880]; // A5, C#6, A5
        const durations = [0.15, 0.15, 0.15];
        const delays = [0, 200, 400];
        
        frequencies.forEach((freq, index) => {
            setTimeout(() => {
                this.playTone(freq, this.volume * 0.8, durations[index], 'sawtooth');
            }, delays[index]);
        });
    }
    
    // Sonido para tickets de alta prioridad - Doble tono
    playHighPriorityAlert() {
        if (!this.enabled) return;
        
        this.playTone(659, this.volume * 0.6, 0.2, 'sine'); // E5
        setTimeout(() => {
            this.playTone(784, this.volume * 0.6, 0.2, 'sine'); // G5
        }, 250);
    }
    
    // Sonido para tickets normales - Tono suave
    playNormalAlert() {
        if (!this.enabled) return;
        
        this.playTone(523, this.volume * 0.4, 0.25, 'sine'); // C5
        setTimeout(() => {
            this.playTone(659, this.volume * 0.3, 0.15, 'sine'); // E5
        }, 150);
    }
    
    // Sonido de éxito - Acorde mayor
    playSuccess() {
        if (!this.enabled) return;
        
        const chord = [523, 659, 784]; // C5, E5, G5
        chord.forEach((freq, index) => {
            setTimeout(() => {
                this.playTone(freq, this.volume * 0.3, 0.5, 'sine');
            }, index * 50);
        });
    }
    
    // Sonido de error - Tono descendente
    playError() {
        if (!this.enabled) return;
        
        this.playTone(400, this.volume * 0.5, 0.3, 'square');
        setTimeout(() => {
            this.playTone(300, this.volume * 0.5, 0.4, 'square');
        }, 200);
    }
    
    // Sonido de notificación suave - Para mensajes informativos
    playInfo() {
        if (!this.enabled) return;
        
        this.playTone(800, this.volume * 0.2, 0.1, 'sine');
        setTimeout(() => {
            this.playTone(1000, this.volume * 0.15, 0.1, 'sine');
        }, 100);
    }
    
    // Función base para reproducir tonos
    playTone(frequency, volume, duration, waveType = 'sine') {
        if (!this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = waveType;
        
        // Envelope para sonido más profesional
        const now = this.audioContext.currentTime;
        gainNode.gain.setValueAtTime(0, now);
        gainNode.gain.linearRampToValueAtTime(volume, now + 0.02);
        gainNode.gain.exponentialRampToValueAtTime(0.001, now + duration);
        
        oscillator.start(now);
        oscillator.stop(now + duration);
    }
    
    // Configurar volumen
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
    }
    
    // Habilitar/deshabilitar sonidos
    setEnabled(enabled) {
        this.enabled = enabled;
    }
    
    // Reproducir sonido según tipo de notificación
    playNotificationSound(priority, type = 'ticket') {
        switch (priority) {
            case 'critica':
            case 'critical':
                this.playCriticalAlert();
                break;
            case 'alta':
            case 'high':
                this.playHighPriorityAlert();
                break;
            case 'media':
            case 'normal':
                this.playNormalAlert();
                break;
            case 'baja':
            case 'low':
                this.playInfo();
                break;
            default:
                this.playNormalAlert();
        }
    }
}

// Crear instancia global
window.soundEffects = new SoundEffects();
