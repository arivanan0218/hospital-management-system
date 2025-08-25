import React, { useState, useEffect, useRef } from 'react';
import { LogOut, User, Settings, Upload, FileText, History, CheckCircle, Plus, X, Mic, MicOff, VolumeX } from 'lucide-react';
import DirectHttpAIMCPService from '../services/directHttpAiMcpService.js';
import MedicalDocumentUpload from './MedicalDocumentUpload.jsx';
import EnhancedMedicalDocumentUpload from './EnhancedMedicalDocumentUpload.jsx';
import MedicalHistoryViewer from './MedicalHistoryViewer.jsx';

const DirectMCPChatbot = ({ user, onLogout }) => {
  // Mobile-responsive CSS classes for consistent mobile experience
  const mobileInputClass = "w-full px-3 py-3 sm:py-2 text-base sm:text-sm";
  const mobileSelectClass = "w-full px-3 py-3 sm:py-2 text-base sm:text-sm";
  
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [showSetup, setShowSetup] = useState(false); // Start with false since auth is handled by parent
  const [showActionButtons, setShowActionButtons] = useState(true); // Track whether to show action buttons
  
  // Configuration state - get API key from environment variables
  const [openaiApiKey] = useState(import.meta.env.VITE_OPENAI_API_KEY || '');
  
  const [serverInfo, setServerInfo] = useState(null);
  const [connectionError, setConnectionError] = useState('');
  const [expandedThinking, setExpandedThinking] = useState({}); // Track which thinking messages are expanded
  const [isInputFocused, setIsInputFocused] = useState(false); // Track input focus state
  const [showPlusMenu, setShowPlusMenu] = useState(false); // Track plus icon dropdown menu
  
  // Voice functionality state
  const [isListening, setIsListening] = useState(false); // Track voice recording state
  const [isProcessingVoice, setIsProcessingVoice] = useState(false); // Track voice processing state
  const [isSpeaking, setIsSpeaking] = useState(false); // Track if AI is currently speaking
  const [lastVoiceInputId, setLastVoiceInputId] = useState(null); // Track the last voice input message ID
  const [isRecording, setIsRecording] = useState(false); // Track audio recording state
  const [mediaRecorder, setMediaRecorder] = useState(null); // Audio recorder instance
  const [audioChunks, setAudioChunks] = useState([]); // Recorded audio chunks
  const [currentAudio, setCurrentAudio] = useState(null); // Current playing audio
  const [microphoneAvailable, setMicrophoneAvailable] = useState(null); // Track microphone availability
  
  // Medical document features
  const [activeTab, setActiveTab] = useState('chat'); // chat, upload, history
  const [selectedPatientId, setSelectedPatientId] = useState(null); // This will store the UUID
  const [selectedPatientNumber, setSelectedPatientNumber] = useState(''); // This will store the patient number (P123456)
  const [searchingPatient, setSearchingPatient] = useState(false);
  const [patientSearchResult, setPatientSearchResult] = useState(null);
  const [patients, setPatients] = useState([]);
  
  // Patient admission popup form
  const [showPatientAdmissionForm, setShowPatientAdmissionForm] = useState(false);
  const [admissionFormData, setAdmissionFormData] = useState({
    first_name: '',
    last_name: '',
    date_of_birth: '',
    gender: '',
    phone: '',
    email: '',
    address: '',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    blood_type: '',
    allergies: '',
    medical_history: ''
  });
  const [isSubmittingAdmission, setIsSubmittingAdmission] = useState(false);
  
  // Department creation popup form
  const [showDepartmentForm, setShowDepartmentForm] = useState(false);
  const [departmentFormData, setDepartmentFormData] = useState({
    name: '',
    description: '',
    head_doctor_id: '', // Foreign key to users table
    floor_number: '',
    phone: '',
    email: ''
  });
  const [isSubmittingDepartment, setIsSubmittingDepartment] = useState(false);
  
  // Staff creation popup form
  const [showStaffForm, setShowStaffForm] = useState(false);
  const [staffFormData, setStaffFormData] = useState({
    user_id: '', // Foreign key to users table
    employee_id: '',
    department_id: '', // Foreign key to departments table
    position: '',
    specialization: '',
    license_number: '',
    hire_date: '',
    salary: '',
    shift_pattern: '', // day, night, rotating
    status: 'active' // active, inactive, on_leave
  });
  const [isSubmittingStaff, setIsSubmittingStaff] = useState(false);
  
  // User creation popup form
  const [showUserForm, setShowUserForm] = useState(false);
  const [userFormData, setUserFormData] = useState({
    username: '',
    email: '',
    password_hash: '', // This should be hashed on backend
    role: '', // admin, doctor, nurse, manager, receptionist
    first_name: '',
    last_name: '',
    phone: '',
    is_active: true
  });
  const [isSubmittingUser, setIsSubmittingUser] = useState(false);
  
  // Room creation popup form
  const [showRoomForm, setShowRoomForm] = useState(false);
  const [roomFormData, setRoomFormData] = useState({
    room_number: '',
    room_type: '', // varchar(20)
    capacity: '',
    floor_number: '', // Integer field in database
    department_id: '' // Foreign key to departments table
  });
  const [isSubmittingRoom, setIsSubmittingRoom] = useState(false);
  
  // Bed creation popup form
  const [showBedForm, setShowBedForm] = useState(false);
  const [bedFormData, setBedFormData] = useState({
    bed_number: '',
    room_id: '',
    bed_type: '',
    status: 'available'
  });
  const [isSubmittingBed, setIsSubmittingBed] = useState(false);
  
  // Equipment creation popup form
  const [showEquipmentForm, setShowEquipmentForm] = useState(false);
  const [equipmentFormData, setEquipmentFormData] = useState({
    equipment_id: '', // Unique equipment ID
    name: '',
    category_id: '', // Foreign key to equipment_categories table
    model: '',
    manufacturer: '',
    serial_number: '',
    purchase_date: '',
    warranty_expiry: '',
    location: '',
    department_id: '', // Foreign key to departments table
    status: 'available', // available, in_use, maintenance, out_of_order
    last_maintenance: '',
    next_maintenance: '',
    cost: '',
    notes: ''
  });
  const [isSubmittingEquipment, setIsSubmittingEquipment] = useState(false);
  
  // Supply creation popup form
  const [showSupplyForm, setShowSupplyForm] = useState(false);
  const [supplyFormData, setSupplyFormData] = useState({
    item_code: '', // Unique item code
    name: '',
    category_id: '', // Foreign key to supply_categories table
    description: '',
    unit_of_measure: '', // Required field - matches database
    minimum_stock_level: '',
    maximum_stock_level: '',
    current_stock: '',
    unit_cost: '', // matches database
    supplier: '',
    expiry_date: '',
    location: ''
  });
  const [isSubmittingSupply, setIsSubmittingSupply] = useState(false);
  
  // Legacy User creation popup form
  const [showLegacyUserForm, setShowLegacyUserForm] = useState(false);
  const [legacyUserFormData, setLegacyUserFormData] = useState({
    name: '',
    email: '',
    address: '',
    phone: ''
  });
  const [isSubmittingLegacyUser, setIsSubmittingLegacyUser] = useState(false);
  
  // Equipment Category creation popup form
  const [showEquipmentCategoryForm, setShowEquipmentCategoryForm] = useState(false);
  const [equipmentCategoryFormData, setEquipmentCategoryFormData] = useState({
    name: '',
    description: ''
  });
  const [isSubmittingEquipmentCategory, setIsSubmittingEquipmentCategory] = useState(false);
  
  // Supply Category creation popup form
  const [showSupplyCategoryForm, setShowSupplyCategoryForm] = useState(false);
  const [supplyCategoryFormData, setSupplyCategoryFormData] = useState({
    name: '',
    description: ''
  });
  const [isSubmittingSupplyCategory, setIsSubmittingSupplyCategory] = useState(false);
  
  // Dropdown options state for foreign keys
  const [departmentOptions, setDepartmentOptions] = useState([]);
  const [userOptions, setUserOptions] = useState([]);
  const [roomOptions, setRoomOptions] = useState([]);
  const [patientOptions, setPatientOptions] = useState([]);
  const [equipmentCategoryOptions, setEquipmentCategoryOptions] = useState([]);
  const [supplyCategoryOptions, setSupplyCategoryOptions] = useState([]);
  const [loadingDropdowns, setLoadingDropdowns] = useState(false);
  
  // Auto-scroll to bottom only when new messages are added, not on timer updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]); // Only trigger on message count change, not message content changes

  // Auto-connect when component mounts if user is authenticated
  useEffect(() => {
    if (user && openaiApiKey && !isConnected && !showSetup) {
      console.log('🔄 Auto-connecting for authenticated user...');
      initializeService();
    }
  }, [user, isConnected, showSetup]); // Dependencies that should trigger auto-connection

  // Component to display thinking duration
  const ThinkingDuration = React.memo(({ startTime }) => {
    const [duration, setDuration] = React.useState(1);
    
    React.useEffect(() => {
      if (!startTime) return;
      
      // Update every 500ms instead of 100ms for better performance
      const interval = setInterval(() => {
        setDuration(Math.ceil((Date.now() - startTime) / 1000));
      }, 500);
      
      return () => clearInterval(interval);
    }, [startTime]);
    
    return <span>{duration}s</span>;
  });
  
  const aiMcpServiceRef = useRef(null);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const lastMessageCountRef = useRef(0);
  const inputFieldRef = useRef(null); // Add ref for input field
  const plusMenuRef = useRef(null); // Add ref for plus menu dropdown
  // Touch / swipe refs for mobile swipe navigation (upload/history -> chat)
  const touchStartXRef = useRef(null);
  const touchStartYRef = useRef(null);
  const touchStartTimeRef = useRef(null);
  const swipeTriggeredRef = useRef(false);

  // Handle touch start (record position/time)
  const handleTouchStart = (e) => {
    try {
      // Ignore if interacting with inputs
      const tag = e.target && e.target.tagName ? e.target.tagName.toUpperCase() : '';
      if (['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON'].includes(tag)) return;
      const t = (e.touches && e.touches[0]) || null;
      if (!t) return;
      touchStartXRef.current = t.clientX;
      touchStartYRef.current = t.clientY;
      touchStartTimeRef.current = Date.now();
    } catch (err) {
      // swallow errors
    }
  };

  // Handle touch end (compute delta and detect swipe-right)
  const handleTouchEnd = (e) => {
    try {
      const t = (e.changedTouches && e.changedTouches[0]) || null;
      if (!t || touchStartXRef.current == null) return;
      const dx = t.clientX - touchStartXRef.current;
      const dy = t.clientY - touchStartYRef.current;
      const dt = Date.now() - (touchStartTimeRef.current || 0);

      const HORIZONTAL_SWIPE_THRESHOLD = 60; // pixels
      const VERTICAL_TOLERANCE = 75; // pixels
      const MAX_SWIPE_TIME = 800; // ms

      // Right swipe with limited vertical movement and reasonable speed
      if (dx > HORIZONTAL_SWIPE_THRESHOLD && Math.abs(dy) < VERTICAL_TOLERANCE && dt < MAX_SWIPE_TIME) {
        // Only switch when not already on chat
        setActiveTab((prev) => (prev === 'chat' ? prev : 'chat'));
      }

      // reset
      touchStartXRef.current = null;
      touchStartYRef.current = null;
      touchStartTimeRef.current = null;
      swipeTriggeredRef.current = false;
    } catch (err) {
      // swallow
    }
  };

  // Handle touch move for earlier detection (helps on scrollable containers)
  const handleTouchMove = (e) => {
    try {
      if (swipeTriggeredRef.current) return;
      const t = (e.touches && e.touches[0]) || null;
      if (!t || touchStartXRef.current == null) return;
      const dx = t.clientX - touchStartXRef.current;
      const dy = t.clientY - touchStartYRef.current;

      const HORIZONTAL_SWIPE_THRESHOLD = 60; // pixels
      const VERTICAL_TOLERANCE = 75; // pixels

      if (dx > HORIZONTAL_SWIPE_THRESHOLD && Math.abs(dy) < VERTICAL_TOLERANCE) {
        swipeTriggeredRef.current = true;
        setActiveTab((prev) => (prev === 'chat' ? prev : 'chat'));
      }
    } catch (err) {
      // swallow
    }
  };

  // Controlled scroll function
  const scrollToBottom = React.useCallback(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);

  // Auto-scroll only when new messages are added, with smart scrolling
  useEffect(() => {
    const currentMessageCount = messages.length;
    if (currentMessageCount > lastMessageCountRef.current) {
      // Only scroll if user is near the bottom (within 100px) or if it's the first message
      if (messagesContainerRef.current) {
        const container = messagesContainerRef.current;
        const isNearBottom = container.scrollTop + container.clientHeight >= container.scrollHeight - 100;
        
        if (isNearBottom || currentMessageCount === 1) {
          setTimeout(scrollToBottom, 50); // Small delay to ensure DOM is updated
        }
      } else {
        setTimeout(scrollToBottom, 50);
      }
    }
    lastMessageCountRef.current = currentMessageCount;
  }, [messages.length, scrollToBottom]);

  // Add keyboard shortcut to focus input (Ctrl/Cmd + /)
  useEffect(() => {
    const handleKeyDown = (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === '/') {
        event.preventDefault();
        if (inputFieldRef.current && isConnected) {
          inputFieldRef.current.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isConnected]);

  // Handle outside clicks for plus menu
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (plusMenuRef.current && !plusMenuRef.current.contains(event.target)) {
        setShowPlusMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Check microphone availability on component mount
  useEffect(() => {
    const checkMicrophoneAvailability = async () => {
      try {
        // Check if microphone APIs are available
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          setMicrophoneAvailable(false);
          console.warn('Microphone API not available - likely due to non-HTTPS connection or browser restrictions');
          return;
        }

        // Check if we're in a secure context
        if (!window.isSecureContext && location.hostname !== 'localhost') {
          setMicrophoneAvailable(false);
          console.warn('Microphone requires HTTPS connection');
          return;
        }

        // Test microphone permissions (this won't trigger permission prompt if denied)
        const permissions = await navigator.permissions.query({ name: 'microphone' });
        
        if (permissions.state === 'denied') {
          setMicrophoneAvailable(false);
          console.warn('Microphone permission denied');
        } else {
          setMicrophoneAvailable(true);
          console.log('Microphone available');
        }
      } catch (error) {
        console.warn('Error checking microphone availability:', error);
        setMicrophoneAvailable(false);
      }
    };

    checkMicrophoneAvailability();
  }, []);

  // Mobile viewport handling to prevent keyboard issues
  useEffect(() => {
    const handleMobileViewport = () => {
      if (isMobileDevice()) {
        // Set CSS custom property for real viewport height
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
        
        // Prevent viewport zoom on input focus
        const viewport = document.querySelector('meta[name=viewport]');
        if (!viewport) {
          const newViewport = document.createElement('meta');
          newViewport.name = 'viewport';
          newViewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover';
          document.head.appendChild(newViewport);
        }
      }
    };

    // Initial setup
    handleMobileViewport();

    // Handle orientation changes and resize
    const handleResize = () => {
      if (isMobileDevice()) {
        setTimeout(handleMobileViewport, 100); // Delay to account for keyboard animation
      }
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
    };
  }, []);

  // Mobile detection utility function
  const isMobileDevice = () => {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
           (window.innerWidth <= 768) || // Also check for small screen width
           ('ontouchstart' in window); // Check for touch capability
  };

  // Function to adjust view when keyboard appears on mobile devices
  const adjustViewForMobileKeyboard = React.useCallback(() => {
    if (isMobileDevice() && inputFieldRef.current) {
      // Add a small delay to allow keyboard to appear
      setTimeout(() => {
        // Scroll the input into view
        inputFieldRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Additional scroll adjustment to ensure input is above keyboard
        const scrollY = window.scrollY || window.pageYOffset;
        window.scrollTo({
          top: Math.max(0, scrollY - 150),
          behavior: 'smooth'
        });
      }, 300);
    }
  }, []);

  // Smart focus function - focuses input but prevents keyboard popup on mobile
  const smartFocusInput = (delay = 100) => {
    setTimeout(() => {
      if (inputFieldRef.current) {
        if (isMobileDevice()) {
          // On mobile: We now want to focus and adjust the view for keyboard
          inputFieldRef.current.focus();
          adjustViewForMobileKeyboard();
        } else {
          // On desktop: normal focus behavior
          inputFieldRef.current.focus();
        }
      }
    }, delay);
  };

  // OpenAI Text-to-Speech function for voice output
  const speakTextWithOpenAI = async (text, isResponseToVoiceInput = false) => {
    // Only speak if this is a response to voice input and we have an API key
    if (!isResponseToVoiceInput || !openaiApiKey.trim()) {
      return;
    }

    // Stop any current audio
    stopCurrentAudio();

    // Clean up text for speech (remove markdown and formatting)
    let cleanText = text
      .replace(/\*\*([^*]+)\*\*/g, '$1') // Remove bold markdown
      .replace(/\*([^*]+)\*/g, '$1') // Remove italic markdown
      .replace(/`([^`]+)`/g, '$1') // Remove code backticks
      .replace(/#{1,6}\s?/g, '') // Remove heading hashtags
      .replace(/---/g, '') // Remove horizontal rules
      .replace(/\n{2,}/g, '\n') // Reduce multiple newlines
      .replace(/🧠|🤔|🔍|🛠️|📊|💡|ℹ️|✅|❌|💥/g, '') // Remove emojis
      .replace(/\[(.*?)\]\(.*?\)/g, '$1') // Convert links to just text
      .replace(/\*\*([^*]+)\*\*/g, '$1') // Additional cleanup
      .replace(/\n/g, ' ') // Replace newlines with spaces
      .replace(/\s+/g, ' ') // Replace multiple spaces with single space
      .trim();

    // Skip speaking if text is too short or just symbols
    if (cleanText.length < 3 || /^[^\w\s]*$/.test(cleanText)) {
      return;
    }

    // Limit text length for TTS (OpenAI has a 4096 character limit)
    if (cleanText.length > 4000) {
      cleanText = cleanText.substring(0, 4000) + '...';
    }

    try {
      setIsSpeaking(true);

      const response = await fetch('https://api.openai.com/v1/audio/speech', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${openaiApiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'tts-1', // Use tts-1 for faster generation, tts-1-hd for higher quality
          input: cleanText,
          voice: 'alloy', // Options: alloy, echo, fable, onyx, nova, shimmer
          response_format: 'mp3',
          speed: 1.0,
        }),
      });

      if (!response.ok) {
        throw new Error(`TTS API error: ${response.status}`);
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      audio.onloadeddata = () => {
        setCurrentAudio(audio);
        audio.play().catch((error) => {
          console.error('Audio playback failed:', error);
          setIsSpeaking(false);
        });
      };

      audio.onended = () => {
        setIsSpeaking(false);
        setCurrentAudio(null);
        URL.revokeObjectURL(audioUrl);
      };

      audio.onerror = (error) => {
        console.error('Audio playback error:', error);
        setIsSpeaking(false);
        setCurrentAudio(null);
        URL.revokeObjectURL(audioUrl);
      };
    } catch (error) {
      console.error('OpenAI TTS error:', error);
      setIsSpeaking(false);

      // Fallback to browser speech synthesis if OpenAI fails
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 0.8;

        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = () => setIsSpeaking(false);

        speechSynthesis.speak(utterance);
      }
    }
  };

  // Function to stop current audio playback
  const stopCurrentAudio = () => {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      setCurrentAudio(null);
    }
    if ('speechSynthesis' in window && speechSynthesis.speaking) {
      speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  };

  // OpenAI Speech-to-Text (Whisper) function
  const transcribeWithOpenAI = async (audioBlob) => {
    if (!openaiApiKey.trim()) {
      throw new Error('OpenAI API key is required for speech recognition');
    }

    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.webm');
    formData.append('model', 'whisper-1');
    formData.append('language', 'en'); // Optional: specify language
    formData.append('response_format', 'json');

    try {
      const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${openaiApiKey}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Whisper API error: ${response.status}`);
      }

      const result = await response.json();
      return result.text;
    } catch (error) {
      console.error('OpenAI Whisper error:', error);
      throw error;
    }
  };

  // Start recording audio for speech-to-text
  const startRecording = async () => {
    try {
      // Stop any current audio playback
      stopCurrentAudio();

      // Check if microphone APIs are available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Microphone access is not available. This may be due to: 1) Non-HTTPS connection (required for microphone access), 2) Browser security restrictions, or 3) Missing microphone permissions.');
      }

      // Check if we're in a secure context (HTTPS or localhost)
      if (!window.isSecureContext && location.hostname !== 'localhost') {
        throw new Error('Microphone access requires HTTPS connection. Please access the site via HTTPS.');
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      const recorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
      });

      const chunks = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        setIsProcessingVoice(true);

        try {
          const transcript = await transcribeWithOpenAI(audioBlob);

          if (transcript && transcript.trim()) {
            setInputMessage(transcript);

            // Show user's voice input message in chat
            const voiceInputId = Date.now();
            const userMsg = {
              id: voiceInputId,
              text: transcript.trim(),
              sender: 'user',
              timestamp: new Date().toLocaleTimeString(),
              isVoiceInput: true,
            };
            setMessages((prev) => [...prev, userMsg]);
            setLastVoiceInputId(voiceInputId);

            // Auto-send the voice input after a short delay
            setTimeout(() => {
              if (transcript.trim() && isConnected && !isLoading) {
                setInputMessage('');
                sendMessageClaudeStyle(transcript.trim(), true);
                setIsProcessingVoice(false);
              } else {
                setIsProcessingVoice(false);
              }
            }, 800);
          } else {
            setIsProcessingVoice(false);
            console.log('No speech detected');
          }
        } catch (error) {
          console.error('Speech transcription failed:', error);
          setIsProcessingVoice(false);

          // Show error message
          const errorMsg = {
            id: Date.now(),
            text: `🎤 **Speech Recognition Error:** ${error.message}. Please try again.`,
            sender: 'ai',
            timestamp: new Date().toLocaleTimeString(),
            isError: true,
          };
          setMessages((prev) => [...prev, errorMsg]);
        }

        // Clean up media stream
        stream.getTracks().forEach((track) => track.stop());
        setAudioChunks([]);
      };

      setMediaRecorder(recorder);
      setAudioChunks(chunks);
      setIsRecording(true);
      setIsListening(true);

      recorder.start();
    } catch (error) {
      console.error('Failed to start recording:', error);
      setIsRecording(false);
      setIsListening(false);

      // Show error message
      const errorMsg = {
        id: Date.now(),
        text: `🎤 **Microphone Error:** ${error.message}. Please check your microphone permissions.`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  // Stop recording audio
  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
    }
    setIsRecording(false);
    setIsListening(false);
  };

  // Voice input toggle function
  const toggleVoiceInput = () => {
    if (!openaiApiKey.trim()) {
      const errorMsg = {
        id: Date.now(),
        text: '🔑 **API Key Required:** Please configure your OpenAI API key to use voice features.',
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMsg]);
      return;
    }

    // If AI is speaking, stop the speech
    if (isSpeaking) {
      stopCurrentAudio();
      return;
    }

    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  /**
   * Initialize the AI-MCP service
   */
  const initializeService = async () => {
    if (!openaiApiKey.trim()) {
      setConnectionError('OpenAI API key not configured in environment variables. Please contact administrator.');
      return;
    }

    setIsLoading(true);
    setConnectionError('');
    
    try {
      aiMcpServiceRef.current = new DirectHttpAIMCPService();
      
      console.log('🚀 Initializing Direct HTTP MCP Service...');
      
      const initialized = await aiMcpServiceRef.current.initialize();
      
      if (initialized) {
        setIsConnected(true);
        setShowSetup(false);
        
        const info = aiMcpServiceRef.current.getServerInfo();
        setServerInfo(info);
        
        setMessages([{
          id: Date.now(),
          text: `👋 Welcome to Hospital Agent! How can I help you today? 🏥`,
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString()
        }]);
        
        // Auto-focus the input field after successful connection (smart focus)
        smartFocusInput(100);
        
      } else {
        throw new Error('Failed to initialize service');
      }
      
    } catch (error) {
      console.error('❌ Initialization failed:', error);
      setConnectionError(`Connection failed: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Load dropdown options for foreign key fields
   */
  const loadDropdownOptions = async () => {
    if (!aiMcpServiceRef.current || loadingDropdowns) return;
    
    setLoadingDropdowns(true);
    try {
      // Load departments
      const departmentsResponse = await aiMcpServiceRef.current.mcpClient.callTool('list_departments', {});
      console.log('🏥 Departments response:', departmentsResponse);
      const departments = departmentsResponse?.result?.content?.[0]?.text 
        ? JSON.parse(departmentsResponse.result.content[0].text)?.result?.data || []
        : departmentsResponse?.result?.data || departmentsResponse || [];
      console.log('🏥 Departments parsed:', departments);
      setDepartmentOptions(Array.isArray(departments) ? departments : []);
      
      // Load users
      const usersResponse = await aiMcpServiceRef.current.mcpClient.callTool('list_users', {});
      console.log('👥 Users response:', usersResponse);
      const users = usersResponse?.result?.content?.[0]?.text 
        ? JSON.parse(usersResponse.result.content[0].text)?.result?.data || []
        : usersResponse?.result?.data || usersResponse || [];
      console.log('👥 Users parsed:', users);
      setUserOptions(Array.isArray(users) ? users : []);
      
      // Load rooms
      const roomsResponse = await aiMcpServiceRef.current.mcpClient.callTool('list_rooms', {});
      console.log('🚪 Rooms response:', roomsResponse);
      const rooms = roomsResponse?.result?.content?.[0]?.text 
        ? JSON.parse(roomsResponse.result.content[0].text)?.result?.data || []
        : roomsResponse?.result?.data || roomsResponse || [];
      console.log('🚪 Rooms parsed:', rooms);
      setRoomOptions(Array.isArray(rooms) ? rooms : []);
      
      // Load patients
      const patientsResponse = await aiMcpServiceRef.current.mcpClient.callTool('list_patients', {});
      const patients = patientsResponse?.result?.content?.[0]?.text 
        ? JSON.parse(patientsResponse.result.content[0].text)?.result?.data || []
        : patientsResponse?.result?.data || patientsResponse || [];
      console.log('🤒 Patients parsed:', patients);
      setPatientOptions(Array.isArray(patients) ? patients : []);
      
      // Load equipment categories
      try {
        const equipmentCategoriesResponse = await aiMcpServiceRef.current.mcpClient.callTool('list_equipment_categories', {});
        const equipmentCategories = equipmentCategoriesResponse?.result?.content?.[0]?.text 
          ? JSON.parse(equipmentCategoriesResponse.result.content[0].text)?.result?.data || []
          : equipmentCategoriesResponse?.result?.data || equipmentCategoriesResponse || [];
        setEquipmentCategoryOptions(Array.isArray(equipmentCategories) ? equipmentCategories : []);
      } catch (e) {
        console.warn('Equipment categories not available:', e);
        setEquipmentCategoryOptions([]);
      }
      
      // Load supply categories
      try {
        const supplyCategoriesResponse = await aiMcpServiceRef.current.mcpClient.callTool('list_supply_categories', {});
        const supplyCategories = supplyCategoriesResponse?.result?.content?.[0]?.text 
          ? JSON.parse(supplyCategoriesResponse.result.content[0].text)?.result?.data || []
          : supplyCategoriesResponse?.result?.data || supplyCategoriesResponse || [];
        setSupplyCategoryOptions(Array.isArray(supplyCategories) ? supplyCategories : []);
      } catch (e) {
        console.warn('Supply categories not available:', e);
        setSupplyCategoryOptions([]);
      }
      
      console.log('✅ Dropdown options loaded successfully');
    } catch (error) {
      console.error('❌ Failed to load dropdown options:', error);
    } finally {
      setLoadingDropdowns(false);
    }
  };

  /**
   * Use OpenAI to intelligently detect user intent for showing popup forms
   * Only specific CREATE tools trigger popup forms, all other tools use AI processing
   */
  const detectIntentWithAI = async (userMessage) => {
    if (!openaiApiKey.trim()) {
      return null; // Fall back to keyword matching if no API key
    }

    try {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${openaiApiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'gpt-3.5-turbo',
          messages: [
            {
              role: 'system',
              content: `You are an intelligent intent detection system for a hospital management application with multi-agent backend tools. 

POPUP FORM TRIGGERS (Only these EXACT 10 CREATE tools should show popup forms):
1. create_user: User creation popup form
2. create_patient: Patient admission popup form  
3. create_legacy_user: Legacy user creation popup form
4. create_department: Department creation popup form
5. create_room: Room creation popup form
6. create_bed: Bed creation popup form
7. create_staff: Staff creation popup form
8. create_equipment: Equipment creation popup form (ONLY this exact tool)
9. create_supply: Supply creation popup form (ONLY this exact tool)

CRITICAL: These tools should use AI processing (NOT popup forms):
- create_equipment_category (AI processing, NOT popup)
- create_supply_category (AI processing, NOT popup)
- All other tools like list, get, update, delete, search, etc.

IMPORTANT DISTINCTION:
- "create equipment" or "add equipment" → create_equipment popup form
- "create equipment category" → ai_processing (no popup)
- "create supply" or "add supply" → create_supply popup form  
- "create supply category" → ai_processing (no popup)

RULES:
1. Only the exact 9 CREATE tools above trigger popup forms
2. Equipment/Supply categories are handled by AI processing
3. All listing, searching, updating, deleting operations use AI processing
4. Staff meetings = AI processing (schedule_meeting tool)

Return ONLY one of these values:
- "create_user" for system user creation
- "create_patient" for patient registration/admission  
- "create_legacy_user" for legacy user creation
- "create_department" for department creation
- "create_room" for room creation
- "create_bed" for bed creation
- "create_staff" for staff hiring/registration
- "create_equipment" for equipment registration/adding new equipment
- "create_supply" for supply registration
- "create_equipment_category" for equipment category creation
- "create_supply_category" for supply category creation
- "ai_processing" for everything else (including equipment usage, staff assignments, updates, searches, etc.)

Examples:
- "Register a new patient" → create_patient
- "Add new staff member" → create_staff  
- "Create cardiology department" → create_department
- "Add new equipment" → create_equipment
- "Register equipment" → create_equipment
- "Create equipment category" → create_equipment_category
- "Add equipment usage for patient" → ai_processing
- "Record equipment usage" → ai_processing
- "Add new supply" → create_supply
- "Create supply category" → create_supply_category
- "Schedule staff meeting" → ai_processing
- "List all patients" → ai_processing
- "Update bed status" → ai_processing`
            },
            {
              role: 'user',
              content: userMessage
            }
          ],
          max_tokens: 50,
          temperature: 0.1
        })
      });

      if (!response.ok) {
        console.warn('Intent detection API call failed:', response.status);
        return null;
      }

      const result = await response.json();
      const intent = result.choices[0].message.content.trim().toLowerCase();
      
      console.log('🤖 AI Intent Detection Result:', userMessage, '->', intent);
      
      // STRICT VALIDATION: Only these exact 12 create tools should show popup forms
      // All other tools use AI processing
      const POPUP_FORM_TOOLS = [
        'create_user',                  // System user creation
        'create_patient',               // Patient registration/admission  
        'create_legacy_user',           // Legacy user creation
        'create_department',            // Department creation
        'create_room',                  // Room creation
        'create_bed',                   // Bed creation
        'create_staff',                 // Staff hiring/registration
        'create_equipment',             // Equipment registration
        'create_supply',                // Supply registration
        'create_equipment_category',    // Equipment category creation
        'create_supply_category'        // Supply category creation
      ];
      
      if (POPUP_FORM_TOOLS.includes(intent)) {
        console.log('✅ POPUP FORM TRIGGERED for:', intent);
        return intent;
      }
      
      console.log('🤖 AI PROCESSING MODE for:', intent || 'unrecognized intent');
      return 'ai_processing'; // Default to AI processing for everything else
    } catch (error) {
      console.warn('Intent detection error:', error);
      return 'ai_processing'; // Default to AI processing on error
    }
  };

  /**
   * Smart conversation flow: 
   * - CREATE tools (create_user, create_patient, etc.) → Show popup forms
   * - ALL OTHER tools (list, search, update, delete, etc.) → Intelligent AI processing
   */
  const sendMessageClaudeStyle = async (customMessage = null, isFromVoiceInput = false) => {
    const messageToSend = customMessage || inputMessage.trim();
    if (!messageToSend || !isConnected || isLoading) return;

    const userMessage = messageToSend;
    if (!customMessage) {
      setInputMessage('');
    }
    setIsLoading(true);
    
    // Hide action buttons after first query
    if (showActionButtons) {
      setShowActionButtons(false);
      
      // Correct viewport after action buttons transition on mobile
      if (isMobileDevice()) {
        setTimeout(() => {
          const vh = window.innerHeight * 0.01;
          document.documentElement.style.setProperty('--vh', `${vh}px`);
          window.scrollTo(0, 0);
          document.body.style.height = '100%';
        }, 600); // Wait for transition to complete (500ms + buffer)
      }
    }

    // Add user message only if it's not from voice input (voice input already adds the message)
    if (!isFromVoiceInput) {
      const userMsg = {
        id: Date.now(),
        text: userMessage,
        sender: 'user',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, userMsg]);
    }

    // 🤖 INTELLIGENT AI INTENT DETECTION FIRST
    try {
      const detectedIntent = await detectIntentWithAI(userMessage);
      
      if (detectedIntent && detectedIntent !== 'ai_processing') {
        setIsLoading(false);
        
        console.log('🎯 POPUP FORM HANDLER - Processing intent:', detectedIntent);
        
        // Show appropriate popup form based on AI detection
        switch (detectedIntent) {
          case 'create_patient':
            console.log('📝 Opening Patient Admission Form');
            setShowPatientAdmissionForm(true);
            const patientMsg = {
              id: Date.now() + 1,
              text: "I detected you want to register a new patient! I've opened the patient admission form for you.",
              sender: 'ai',
              timestamp: new Date().toLocaleTimeString()
            };
            setMessages(prev => [...prev, patientMsg]);
            return;
            
          case 'create_department':
            console.log('🏥 Opening Department Creation Form');
            await loadDropdownOptions(); // Load users for head_doctor_id
            setShowDepartmentForm(true);
            const deptMsg = {
              id: Date.now() + 1,
              text: "I detected you want to create a new department! I've opened the department creation form for you. The dropdown menus are being populated with available users for the head doctor selection.",
              sender: 'ai',
              timestamp: new Date().toLocaleTimeString()
            };
            setMessages(prev => [...prev, deptMsg]);
            return;
            
          case 'create_staff':
            console.log('👥 Opening Staff Creation Form');
            await loadDropdownOptions(); // Load users and departments
            setShowStaffForm(true);
            const staffMsg = {
              id: Date.now() + 1,
              text: "I detected you want to add a new staff member! I've opened the staff creation form for you. Please select a user and department from the dropdown menus.",
              sender: 'ai',
              timestamp: new Date().toLocaleTimeString()
            };
            setMessages(prev => [...prev, staffMsg]);
            return;
            
          case 'create_user':
            console.log('👤 Opening User Creation Form');
            setShowUserForm(true);
            const userMsg = {
              id: Date.now() + 1,
              text: "I detected you want to create a new user! I've opened the user creation form for you. This form doesn't require foreign key selections.",
              sender: 'ai',
              timestamp: new Date().toLocaleTimeString()
            };
            setMessages(prev => [...prev, userMsg]);
            return;
            
          case 'create_room':
            console.log('🏠 Opening Room Creation Form');
            await loadDropdownOptions(); // Load departments
            setShowRoomForm(true);
            const roomMsg = {
              id: Date.now() + 1,
              text: "I detected you want to create a new room! I've opened the room creation form for you. Please select a department from the dropdown menu.",
              sender: 'ai',
              timestamp: new Date().toLocaleTimeString()
            };
            setMessages(prev => [...prev, roomMsg]);
            return;
            
          case 'create_bed':
            console.log('🛏️ Opening Bed Creation Form');
            await loadDropdownOptions(); // Load rooms
            setShowBedForm(true);
            const bedMsg = {
              id: Date.now() + 1,
              text: "I detected you want to add a new bed! I've opened the bed creation form for you. Please select a room from the dropdown menu.",
              sender: 'ai',
              timestamp: new Date().toLocaleTimeString()
            };
            setMessages(prev => [...prev, bedMsg]);
            return;
            
          case 'create_equipment':
            console.log('⚙️ Opening Equipment Creation Form');
            await loadDropdownOptions(); // Load departments and categories
            setShowEquipmentForm(true);
            const equipMsg = {
              id: Date.now() + 1,
              text: "I detected you want to add new equipment! I've opened the equipment creation form for you. Please select a department and category from the dropdown menus.",
              sender: 'ai',
              timestamp: new Date().toLocaleTimeString()
            };
            setMessages(prev => [...prev, equipMsg]);
            return;
            
          case 'create_supply':
            console.log('📦 Opening Supply Creation Form');
            await loadDropdownOptions(); // Load categories
            setShowSupplyForm(true);
            const supplyMsg = {
              id: Date.now() + 1,
              text: "I detected you want to add new supplies! I've opened the supply creation form for you. Please select a category from the dropdown menu.",
              sender: 'ai',
              timestamp: new Date().toLocaleTimeString()
            };
            setMessages(prev => [...prev, supplyMsg]);
            return;
            
          case 'create_equipment_category':
            console.log('🏷️ Opening Equipment Category Creation Form');
            setShowEquipmentCategoryForm(true);
            const equipCatMsg = {
              id: Date.now() + 1,
              text: "I detected you want to create an equipment category! I've opened the equipment category creation form for you. Please provide a name and optional description.",
              sender: 'ai',
              timestamp: new Date().toLocaleTimeString()
            };
            setMessages(prev => [...prev, equipCatMsg]);
            return;
            
          case 'create_supply_category':
            console.log('🏷️ Opening Supply Category Creation Form');
            setShowSupplyCategoryForm(true);
            const supplyCatMsg = {
              id: Date.now() + 1,
              text: "I detected you want to create a supply category! I've opened the supply category creation form for you. Please provide a name and optional description.",
              sender: 'ai',
              timestamp: new Date().toLocaleTimeString()
            };
            setMessages(prev => [...prev, supplyCatMsg]);
            return;
            
          case 'create_legacy_user':
            console.log('👤 Opening Legacy User Creation Form');
            setShowLegacyUserForm(true);
            const legacyMsg = {
              id: Date.now() + 1,
              text: "I detected you want to create a legacy user! I've opened the legacy user creation form for you.",
              sender: 'ai',
              timestamp: new Date().toLocaleTimeString()
            };
            setMessages(prev => [...prev, legacyMsg]);
            return;
            
          default:
            console.warn('⚠️ Unknown popup intent detected:', detectedIntent, '- Falling back to AI processing');
            // Fall through to AI processing
        }
      }
      
      // If AI detected 'ai_processing' or no specific form intent, proceed with intelligent AI processing
      if (detectedIntent === 'ai_processing' || !detectedIntent) {
        console.log('🤖 AI PROCESSING MODE: Using intelligent backend agent tools for:', userMessage);
        // Skip fallback keyword detection and go directly to AI processing
      }
      
    } catch (error) {
      console.warn('AI intent detection failed, proceeding with AI processing:', error);
    }

    // For all other requests, use intelligent AI processing with the backend agents
    // The AI will analyze the request and call the appropriate backend tools automatically
    console.log('🤖 Proceeding with Intelligent AI Processing');

    let thinkingMessageId = null;
    let thinkingStartTime = null;

    try {
      // Show contextual thinking for all requests (since AI will determine the right tools)
      thinkingStartTime = Date.now();
      thinkingMessageId = Date.now() + Math.random();
      
      // Generate contextual thinking message based on user input
      let thinkingText = 'Processing ';
      if (userMessage.toLowerCase().includes('list') || userMessage.toLowerCase().includes('show')) {
        thinkingText = 'Retrieving ';
      } else if (userMessage.toLowerCase().includes('find') || userMessage.toLowerCase().includes('search')) {
        thinkingText = 'Searching for ';
      } else if (userMessage.toLowerCase().includes('update') || userMessage.toLowerCase().includes('assign')) {
        thinkingText = 'Updating ';
      } else if (userMessage.toLowerCase().includes('meeting') || userMessage.toLowerCase().includes('schedule')) {
        thinkingText = 'Scheduling ';
      }

      // Add the subject based on keywords
      if (userMessage.toLowerCase().includes('patient')) {
        thinkingText += 'patient information';
      } else if (userMessage.toLowerCase().includes('staff')) {
        thinkingText += 'staff records';
      } else if (userMessage.toLowerCase().includes('bed')) {
        thinkingText += 'bed information';
      } else if (userMessage.toLowerCase().includes('department')) {
        thinkingText += 'department data';
      } else if (userMessage.toLowerCase().includes('equipment')) {
        thinkingText += 'equipment status';
      } else if (userMessage.toLowerCase().includes('supply')) {
        thinkingText += 'supply inventory';
      } else if (userMessage.toLowerCase().includes('meeting')) {
        thinkingText += 'meeting details';
      } else {
        thinkingText += 'your request';
      }

      const thinkingMessage = {
        id: thinkingMessageId,
        text: thinkingText,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString(),
        isThinking: true,
        startTime: thinkingStartTime
      };
      setMessages(prev => [...prev, thinkingMessage]);

      // Process the request
      const response = await aiMcpServiceRef.current.processRequest(userMessage);
      
      // Remove thinking message if present
      if (thinkingMessageId) {
        setMessages(prev => prev.filter(msg => msg.id !== thinkingMessageId));
        
        // Remove artificial delay for faster response
        // await new Promise(resolve => setTimeout(resolve, 200));
      }
      
      if (response.success) {
        // Show tool execution if tools were called
        if (response.functionCalls && response.functionCalls.length > 0) {
          response.functionCalls.forEach((call, index) => {
            // Create contextual thinking message for each tool
            let thinkingText = '';
            switch (call.function) {
              case 'search_patients':
                thinkingText = `Great! I found a patient named ${call.arguments?.first_name || 'the patient'}.`;
                break;
              case 'list_patients':
                thinkingText = 'I can see the patient registry with all available patients.';
                break;
              case 'list_beds':
                thinkingText = "Identified patient's bed assignment and prepared overview.";
                break;
              case 'list_departments':
                thinkingText = 'I can see all hospital departments and their information.';
                break;
              case 'list_staff':
                thinkingText = 'I can see the hospital staff directory.';
                break;
              case 'get_patient_by_id':
                thinkingText = `Found detailed information for patient ${call.arguments?.patient_id || 'ID'}.`;
                break;
              case 'get_staff_by_id':
                thinkingText = `Located staff member ${call.arguments?.staff_id || 'information'}.`;
                break;
              case 'create_patient':
                thinkingText = 'Successfully created new patient record.';
                break;
              default:
                thinkingText = `Executed ${call.function.replace(/_/g, ' ')} successfully.`;
            }

            const toolMessage = {
              id: Date.now() + index + 100,
              text: thinkingText,
              sender: 'ai',
              timestamp: new Date().toLocaleTimeString(),
              isThinking: true,
              toolFunction: call.function,
              startTime: Date.now() // No artificial delay
            };
            setMessages(prev => [...prev, toolMessage]);
          });
        }

        // Final response with the processed data
        const finalResponse = {
          id: Date.now() + 1000,
          text: response.response || response.message || 'Here\'s what I found based on your request.',
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString(),
          isFinalAnswer: true
        };
        setMessages(prev => [...prev, finalResponse]);

        // If this is a response to voice input, speak the response
        if (isFromVoiceInput) {
          setTimeout(() => {
            speakTextWithOpenAI(response.response || response.message || 'Here\'s what I found based on your request.', true);
          }, 500);
        }
        
      } else {
        // Direct error response without thinking for simple errors
        const errorResponse = {
          id: Date.now() + 1000,
          text: `I apologize, but I encountered an error: ${response.error || 'Unknown error occurred'}\n\nPlease try rephrasing your request or let me know if you need help with something specific.`,
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString(),
          isError: true
        };
        setMessages(prev => [...prev, errorResponse]);

        // If this is a response to voice input, speak the error message
        if (isFromVoiceInput) {
          setTimeout(() => {
            speakTextWithOpenAI(`I apologize, but I encountered an error: ${response.error || 'Unknown error occurred'}. Please try rephrasing your request.`, true);
          }, 500);
        }
      }
      
    } catch (error) {
      console.error('❌ Send message failed:', error);
      
      // Remove thinking message if present
      if (thinkingMessageId) {
        setMessages(prev => prev.filter(msg => msg.id !== thinkingMessageId));
      }

      // Direct error message
      const errorMsg = {
        id: Date.now() + 1000,
        text: `I'm having trouble processing your request: ${error.message}\n\nThis might be a temporary connection issue. Please try again in a moment.`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMsg]);

      // If this is a response to voice input, speak the error message
      if (isFromVoiceInput) {
        setTimeout(() => {
          speakTextWithOpenAI(`I'm having trouble processing your request. This might be a temporary connection issue. Could you please try again?`, true);
        }, 500);
      }
    } finally {
      setIsLoading(false);
      
      // Auto-focus the input field after AI response (smart focus prevents mobile keyboard popup)
      smartFocusInput(100);
    }
  };

  /**
   * Format message text to render markdown formatting and detect discharge reports
   */
  const formatMessageText = (text) => {
    if (!text) return '';
    
    // Check if this message contains a discharge report (but exclude download success messages)
    const isDischargeReport = (text.includes('### Patient Discharge Report') || 
                              text.includes('**Report Number:**') || 
                              text.match(/DR-\d{8}-[A-F0-9]{8}/)) &&
                              !text.includes('PDF Download Complete') &&
                              !text.includes('downloaded to your Downloads folder');
    
    let formattedText = text
      // Bold formatting: **text** -> <strong>text</strong>
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Italic formatting: *text* -> <em>text</em>
      .replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>')
      // Convert line breaks to <br> tags
      .replace(/\n/g, '<br>')
      // Handle bullet points with proper spacing
      .replace(/^• (.*$)/gm, '<div class="ml-4">• $1</div>')
      // Handle double spaces
      .replace(/\s{2}/g, '&nbsp;&nbsp;');
    
    // If this is a discharge report, extract the report number and add download button
    if (isDischargeReport) {
      const reportNumberMatch = text.match(/DR-\d{8}-[A-F0-9]{8}/);
      if (reportNumberMatch && !formattedText.includes('downloadDischargeReportPDF')) {
        const reportNumber = reportNumberMatch[0];
        
        // Add download button HTML after the formatted text
        formattedText += `
          <div class="mt-1 px-3 py-1.5 bg-gray-800 border border-gray-600 rounded-lg">
            <div class="flex items-center justify-between">
              <div class="text-xs text-gray-300 flex items-center space-x-1.5">
                <span class="w-1.5 h-1.5 bg-green-400 rounded-full"></span>
                <span><strong>Report Generated: ${reportNumber}</strong></span>
              </div>
              <button 
                onclick="downloadDischargeReportPDF('${reportNumber}')"
                class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded-lg font-medium transition-all duration-200 flex items-center space-x-1.5 shadow-md hover:shadow-lg"
                title="Download this discharge report as PDF"
              >
                <span class="text-xs">📥</span>
                <span>Download as PDF</span>
              </button>
            </div>
          </div>
        `;
      }
    }
    
    return formattedText;
  };

  /**
   * Download discharge report as PDF - called from dynamically generated buttons
   */
  const downloadDischargeReportPDF = async (reportNumber) => {
    try {
      console.log('📥 Downloading discharge report PDF:', reportNumber);
      
      // Show loading message in chat
      const loadingMessage = {
        id: Date.now() + Math.random(),
        text: `⏳ Downloading discharge report ${reportNumber} as PDF...`,
        sender: 'assistant',
        timestamp: new Date(),
        isLoading: true
      };
      setMessages(prev => [...prev, loadingMessage]);
      
      // Import PDFDownloadManager
      const PDFDownloadManager = (await import('../utils/pdfDownloadManager.js')).default;
      const pdfManager = new PDFDownloadManager();
      
      // Extract patient name from the last few messages if available
      let patientName = 'Patient';
      const recentMessages = messages.slice(-5);
      for (const msg of recentMessages) {
        const nameMatch = msg.text.match(/Patient:\s*([^,\n]+)/i) || 
                         msg.text.match(/Name:\s*([^,\n]+)/i) ||
                         msg.text.match(/\*\*Name:\*\*\s*([^,\n]+)/i);
        if (nameMatch) {
          patientName = nameMatch[1].trim();
          break;
        }
      }
      
      // Download the PDF
      const result = await pdfManager.downloadDischargeReportPDF(reportNumber, patientName);
      
      // Remove loading message
      setMessages(prev => prev.filter(msg => msg.id !== loadingMessage.id));
      
      if (result.success) {
        // Add success message
        const successMessage = {
          id: Date.now() + Math.random(),
          text: `✅ **PDF Download Complete**\n\n📁 **File:** ${result.filename}\n📊 **Size:** ${pdfManager.formatBytes(result.fileSize)}\n💾 **Saved to:** Local browser storage\n\n🎯 The PDF has been automatically downloaded to your Downloads folder and saved in local storage for future access.`,
          sender: 'assistant',
          timestamp: new Date(),
          isFinalAnswer: true
        };
        setMessages(prev => [...prev, successMessage]);
      } else {
        // Add error message
        const errorMessage = {
          id: Date.now() + Math.random(),
          text: `❌ **Download Failed**\n\nError: ${result.error}\n\nPlease try again or contact support if the issue persists.`,
          sender: 'assistant',
          timestamp: new Date(),
          isError: true
        };
        setMessages(prev => [...prev, errorMessage]);
      }
      
    } catch (error) {
      console.error('❌ PDF download error:', error);
      
      // Remove any loading messages
      setMessages(prev => prev.filter(msg => !msg.isLoading));
      
      // Add error message
      const errorMessage = {
        id: Date.now() + Math.random(),
        text: `❌ **Download Error**\n\nFailed to download PDF: ${error.message}\n\nPlease try again later.`,
        sender: 'assistant',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  // Make the download function globally accessible for the dynamically generated buttons
  useEffect(() => {
    window.downloadDischargeReportPDF = downloadDischargeReportPDF;
    
    // Cleanup when component unmounts
    return () => {
      delete window.downloadDischargeReportPDF;
    };
  }, [messages]); // Re-register when messages change to capture current state

  // Handle mobile viewport and keyboard behavior
  useEffect(() => {
    if (typeof window !== 'undefined' && isMobileDevice()) {
      // Set viewport height custom property for mobile
      const setVH = () => {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
        
        // Force height to fill entire viewport
        document.documentElement.style.height = '100%';
        document.body.style.height = '100%';
        document.body.style.minHeight = '100vh';
        document.body.style.minHeight = '100dvh';
      };
      
      // Set initial viewport height MULTIPLE TIMES to ensure it takes effect
      setVH();
      setTimeout(setVH, 100);  // Retry after 100ms
      setTimeout(setVH, 300);  // Retry after 300ms
      setTimeout(setVH, 1000); // Final retry after 1 second
      
      // Prevent body scroll on mobile, but allow input to move with keyboard
      document.body.style.overflow = 'hidden';
      document.body.style.backgroundColor = '#1a1a1a';
      document.documentElement.style.backgroundColor = '#1a1a1a';
      document.body.style.margin = '0';
      document.body.style.padding = '0';
      
      // Force immediate layout correction
      window.scrollTo(0, 0);
      
      // Throttled resize handler
      let timeoutId;
      const handleResize = () => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
          setVH();
          // Check if resize is likely due to keyboard appearing
          const wasResizedByKeyboard = window.innerHeight < window.outerHeight * 0.75;
          
          if (wasResizedByKeyboard && isInputFocused) {
            // Ensure input is visible above keyboard
            adjustViewForMobileKeyboard();
          }
        }, 150);
      };
      
      // Listen for viewport changes
      window.addEventListener('resize', handleResize);
      window.addEventListener('orientationchange', () => {
        setTimeout(setVH, 500); // Delay for orientation change
      });
      
      // Force layout correction on load complete
      window.addEventListener('load', () => {
        setTimeout(setVH, 100);
        window.scrollTo(0, 0);
      });
      
      // Also trigger on DOM content loaded
      if (document.readyState === 'complete') {
        setTimeout(setVH, 100);
      } else {
        window.addEventListener('DOMContentLoaded', () => {
          setTimeout(setVH, 100);
        });
      }
      
      // Enhanced handling for input focus
      const handleFocusIn = (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
          // Small delay to allow keyboard to show up
          setTimeout(() => {
            // Scroll input into view when keyboard appears
            e.target.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Additional adjustments to ensure input is above keyboard
            if (e.target === inputFieldRef.current) {
              adjustViewForMobileKeyboard();
            }
          }, 300);
        }
      };
      
      // Handle keyboard hide event
      const handleFocusOut = () => {
        setTimeout(() => {
          setVH();
          document.body.style.backgroundColor = '#1a1a1a';
          document.documentElement.style.backgroundColor = '#1a1a1a';
          document.body.style.height = '100%';
          document.body.style.minHeight = '100vh';
          window.scrollTo(0, 0);
        }, 150);
      };
      
      document.addEventListener('focusin', handleFocusIn);
      document.addEventListener('focusout', handleFocusOut);
      
      // Cleanup
      return () => {
        window.removeEventListener('resize', handleResize);
        window.removeEventListener('orientationchange', handleResize);
        window.removeEventListener('load', setVH);
        window.removeEventListener('DOMContentLoaded', setVH);
        document.removeEventListener('focusin', handleFocusIn);
        document.removeEventListener('focusout', handleFocusOut);
        clearTimeout(timeoutId);
        
        // Reset body styles
        document.body.style.overflow = '';
        document.body.style.backgroundColor = '';
        document.documentElement.style.backgroundColor = '';
        document.body.style.height = '';
        document.body.style.minHeight = '';
        document.body.style.margin = '';
        document.body.style.padding = '';
        document.documentElement.style.height = '';
      };
    }
  }, [isInputFocused, adjustViewForMobileKeyboard]);

  // Force layout correction after component mount - fixes initial blank space
  useEffect(() => {
    if (typeof window !== 'undefined' && isMobileDevice()) {
      const forceLayoutCorrection = () => {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
        document.body.style.height = '100%';
        document.body.style.minHeight = '100vh';
        document.documentElement.style.height = '100%';
        window.scrollTo(0, 0);
      };
      
      // Multiple attempts to ensure the layout corrects
      const timeouts = [
        setTimeout(forceLayoutCorrection, 50),
        setTimeout(forceLayoutCorrection, 200),
        setTimeout(forceLayoutCorrection, 500),
        setTimeout(forceLayoutCorrection, 1500)
      ];
      
      return () => {
        timeouts.forEach(timeout => clearTimeout(timeout));
      };
    }
  }, [isConnected]); // Run when connection state changes

  // Fix viewport when action buttons visibility changes
  useEffect(() => {
    if (!showActionButtons && isMobileDevice()) {
      // Delay to allow transition to complete
      const timer = setTimeout(() => {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
        document.body.style.height = '100%';
        document.body.style.minHeight = '100vh';
        window.scrollTo(0, 0);
      }, 600); // Wait for CSS transition
      
      return () => clearTimeout(timer);
    }
  }, [showActionButtons]);

  /**
   * Handle sending messages with Claude-style conversation flow
   */
  const handleSendMessage = () => {
    sendMessageClaudeStyle();
  };

  /**
   * Format MCP data responses for clean display
   */
  // eslint-disable-next-line no-unused-vars
  const formatMCPData = (data) => {
    if (!data) return '❌ No data available\n';
    
    console.log('🔍 formatMCPData received:', data); // Debug log
    
    // Handle MCP response array format
    if (Array.isArray(data)) {
      // Check if it's an array of MCP response objects with type and text
      if (data.length > 0 && data[0].type === 'text' && data[0].text) {
        try {
          const parsedData = JSON.parse(data[0].text);
          console.log('🔍 Parsed JSON from MCP array:', parsedData); // Debug log
          return formatMCPData(parsedData); // Recursive call with parsed data
        } catch (e) {
          console.log('🔍 Failed to parse JSON from MCP array:', e); // Debug log
          return `${data[0].text}\n`;
        }
      }
      
      // Handle regular array
      let result = `📋 **DATA RESULTS**\n📊 **Found ${data.length} Item(s)**\n\n`;
      data.forEach((item, i) => {
        result += `${i + 1}. ${formatResultItem(item)}\n`;
      });
      return result;
    }
    
    // Handle nested structure like { "patients": [...], "count": N }
    if (data.patients && Array.isArray(data.patients)) {
      const patients = data.patients;
      let result = `👥 **PATIENT REGISTRY**\n📊 **Found ${patients.length} Patient(s)**\n\n`;
      
      patients.forEach((patient, i) => {
        result += `🏥 **${i + 1}. ${patient.first_name} ${patient.last_name}**\n`;
        result += `   📋 **Patient ID:** ${patient.patient_number}\n`;
        if (patient.date_of_birth) result += `   📅 **Date of Birth:** ${patient.date_of_birth}\n`;
        if (patient.gender) result += `   👤 **Gender:** ${patient.gender}\n`;
        if (patient.phone) result += `   📞 **Phone:** ${patient.phone}\n`;
        if (patient.email) result += `   📧 **Email:** ${patient.email}\n`;
        if (patient.address) result += `   🏠 **Address:** ${patient.address}\n`;
        if (patient.blood_type) result += `   🩸 **Blood Type:** ${patient.blood_type}\n`;
        if (patient.allergies && patient.allergies !== 'null' && patient.allergies !== null) {
          result += `   ⚠️ **Allergies:** ${patient.allergies}\n`;
        }
        if (patient.medical_history && patient.medical_history !== 'null' && patient.medical_history !== null) {
          result += `   📝 **Medical History:** ${patient.medical_history}\n`;
        }
        if (patient.emergency_contact_name) {
          result += `   🆘 **Emergency Contact:** ${patient.emergency_contact_name}`;
          if (patient.emergency_contact_phone) result += ` (${patient.emergency_contact_phone})`;
          result += '\n';
        }
        result += '\n';
      });
      
      if (data.count && data.count !== patients.length) {
        result += `📈 *Total in database: ${data.count} patients*\n`;
      }
      
      result += `\n💡 **Quick Actions:**\n`;
      result += `• Create new patient: "Add new patient [Name]"\n`;
      result += `• Search patient: "Find patient [Name/ID]"\n`;
      result += `• Update records: "Update patient [ID]"\n`;
      
      return result;
    }
    
    // Handle departments
    if (data.departments && Array.isArray(data.departments)) {
      const departments = data.departments;
      let result = `🏢 **HOSPITAL DEPARTMENTS**\n📊 **Found ${departments.length} Department(s)**\n\n`;
      
      departments.forEach((dept, i) => {
        result += `🏥 **${i + 1}. ${dept.name}**\n`;
        result += `   🆔 **Department ID:** ${dept.department_id}\n`;
        if (dept.floor_number) result += `   🏗️ **Floor:** ${dept.floor_number}\n`;
        if (dept.phone) result += `   📞 **Phone:** ${dept.phone}\n`;
        if (dept.email) result += `   📧 **Email:** ${dept.email}\n`;
        if (dept.description) result += `   📝 **Description:** ${dept.description}\n`;
        if (dept.head_doctor_id) result += `   👨‍⚕️ **Head Doctor ID:** ${dept.head_doctor_id}\n`;
        result += '\n';
      });
      
      result += `\n💡 **Department Actions:**\n`;
      result += `• Create department: "Add new department [Name]"\n`;
      result += `• Assign staff: "Assign staff to [Department]"\n`;
      result += `• Update info: "Update department [ID]"\n`;
      
      return result;
    }
    
    // Handle staff
    if (data.staff && Array.isArray(data.staff)) {
      const staff = data.staff;
      let result = `👨‍⚕️ **HOSPITAL STAFF**\n📊 **Found ${staff.length} Staff Member(s)**\n\n`;
      
      staff.forEach((member, i) => {
        result += `👤 **${i + 1}. ${member.position}**\n`;
        result += `   🆔 **Employee ID:** ${member.employee_id}\n`;
        if (member.department_id) result += `   🏢 **Department:** ${member.department_id}\n`;
        if (member.specialization) result += `   🎯 **Specialization:** ${member.specialization}\n`;
        if (member.status) result += `   📊 **Status:** ${member.status === 'active' ? '✅ Active' : '⏸️ Inactive'}\n`;
        if (member.hire_date) result += `   📅 **Hire Date:** ${member.hire_date}\n`;
        if (member.shift_pattern) result += `   ⏰ **Shift Pattern:** ${member.shift_pattern}\n`;
        result += '\n';
      });
      
      result += `\n💡 **Staff Actions:**\n`;
      result += `• Add staff: "Add new staff member"\n`;
      result += `• Schedule shifts: "Update staff schedule"\n`;
      result += `• Assign department: "Transfer staff to [Department]"\n`;
      
      return result;
    }
    
    // Handle beds
    if (data.beds && Array.isArray(data.beds)) {
      const beds = data.beds;
      const availableBeds = beds.filter(bed => bed.status === 'available').length;
      const occupiedBeds = beds.filter(bed => bed.status === 'occupied').length;
      
      let result = `🛏️ **BED MANAGEMENT**\n📊 **Found ${beds.length} Bed(s)** | ✅ ${availableBeds} Available | 🔴 ${occupiedBeds} Occupied\n\n`;
      
      beds.forEach((bed, i) => {
        const statusIcon = bed.status === 'available' ? '✅' : bed.status === 'occupied' ? '🔴' : '⚠️';
        result += `${statusIcon} **${i + 1}. Bed ${bed.bed_number}**\n`;
        if (bed.room_id) result += `   🏠 **Room:** ${bed.room_id}\n`;
        if (bed.status) result += `   📊 **Status:** ${bed.status.toUpperCase()}\n`;
        if (bed.bed_type) result += `   🛏️ **Type:** ${bed.bed_type}\n`;
        if (bed.patient_id) result += `   👤 **Current Patient:** ${bed.patient_id}\n`;
        result += '\n';
      });
      
      if (availableBeds === 0) {
        result += `\n🚨 **ALERT: NO AVAILABLE BEDS**\n`;
        result += `⚡ **Emergency Actions:**\n`;
        result += `• Check room capacity for emergency beds\n`;
        result += `• Review discharge schedule\n`;
        result += `• Contact bed management team\n`;
      } else {
        result += `\n💡 **Bed Actions:**\n`;
        result += `• Assign patient: "Assign bed [Number] to patient [ID]"\n`;
        result += `• Discharge patient: "Discharge bed [Number]"\n`;
        result += `• Create emergency bed: "Add emergency bed"\n`;
      }
      
      return result;
    }
    
    // Handle equipment
    if (data.equipment && Array.isArray(data.equipment)) {
      const equipment = data.equipment;
      let result = `🏥 **MEDICAL EQUIPMENT**\n📊 **Found ${equipment.length} Equipment Item(s)**\n\n`;
      
      equipment.forEach((item, i) => {
        result += `⚕️ **${i + 1}. ${item.name}**\n`;
        if (item.equipment_id) result += `   🆔 **Equipment ID:** ${item.equipment_id}\n`;
        if (item.category_id) result += `   📂 **Category:** ${item.category_id}\n`;
        if (item.manufacturer) result += `   🏭 **Manufacturer:** ${item.manufacturer}\n`;
        if (item.model) result += `   📱 **Model:** ${item.model}\n`;
        if (item.location) result += `   📍 **Location:** ${item.location}\n`;
        if (item.status) {
          const statusIcon = item.status === 'operational' ? '✅' : item.status === 'maintenance' ? '🔧' : '❌';
          result += `   ${statusIcon} **Status:** ${item.status.toUpperCase()}\n`;
        }
        result += '\n';
      });
      
      result += `\n💡 **Equipment Actions:**\n`;
      result += `• Schedule maintenance: "Maintain equipment [ID]"\n`;
      result += `• Update status: "Update equipment [ID] status"\n`;
      result += `• Add equipment: "Add new equipment"\n`;
      
      return result;
    }
    
    // Handle supplies
    if (data.supplies && Array.isArray(data.supplies)) {
      const supplies = data.supplies;
      const lowStock = supplies.filter(item => item.current_stock <= item.minimum_stock_level).length;
      
      let result = `📦 **MEDICAL SUPPLIES**\n📊 **Found ${supplies.length} Supply Item(s)**`;
      if (lowStock > 0) result += ` | ⚠️ ${lowStock} Low Stock`;
      result += `\n\n`;
      
      supplies.forEach((item, i) => {
        const stockIcon = item.current_stock <= item.minimum_stock_level ? '⚠️' : '✅';
        result += `${stockIcon} **${i + 1}. ${item.name}**\n`;
        if (item.item_code) result += `   🆔 **Item Code:** ${item.item_code}\n`;
        if (item.current_stock !== undefined) result += `   📊 **Current Stock:** ${item.current_stock}\n`;
        if (item.unit_of_measure) result += `   📏 **Unit:** ${item.unit_of_measure}\n`;
        if (item.supplier) result += `   🏢 **Supplier:** ${item.supplier}\n`;
        if (item.location) result += `   📍 **Location:** ${item.location}\n`;
        if (item.expiry_date) result += `   ⏰ **Expiry Date:** ${item.expiry_date}\n`;
        result += '\n';
      });
      
      result += `\n💡 **Supply Actions:**\n`;
      result += `• Restock: "Update stock for [Item Code]"\n`;
      result += `• Add supply: "Add new supply item"\n`;
      result += `• Check expiry: "Show expiring supplies"\n`;
      
      return result;
    }
    
    // Handle single objects
    if (typeof data === 'object') {
      return `✅ **RESULT:**\n${formatResultItem(data)}\n`;
    }
    
    // Handle simple values
    return `ℹ️ **INFO:** ${String(data)}\n`;
  };

  /**
   * Format individual result items for display
   */
  const formatResultItem = (item) => {
    if (!item) return 'No data';
    
    if (typeof item === 'string') {
      return item;
    }
    
    if (typeof item === 'object') {
      // For patient objects
      if (item.first_name && item.last_name) {
        let patientInfo = `${item.first_name} ${item.last_name}`;
        if (item.patient_number) patientInfo += ` (#${item.patient_number})`;
        if (item.date_of_birth) patientInfo += ` • Born: ${item.date_of_birth}`;
        if (item.phone) patientInfo += ` • Phone: ${item.phone}`;
        if (item.blood_type) patientInfo += ` • Blood Type: ${item.blood_type}`;
        return patientInfo;
      }
      // For department objects
      if (item.name && item.department_id) {
        let deptInfo = `${item.name} (ID: ${item.department_id})`;
        if (item.floor_number) deptInfo += ` • Floor ${item.floor_number}`;
        if (item.phone) deptInfo += ` • Phone: ${item.phone}`;
        return deptInfo;
      }
      // For staff objects
      if (item.user_id && item.position) {
        let staffInfo = `${item.position}`;
        if (item.employee_id) staffInfo += ` (#${item.employee_id})`;
        if (item.specialization) staffInfo += ` • ${item.specialization}`;
        if (item.department_id) staffInfo += ` • Dept: ${item.department_id}`;
        return staffInfo;
      }
      // For bed objects
      if (item.bed_number) {
        let bedInfo = `Bed ${item.bed_number}`;
        if (item.room_id) bedInfo += ` (Room ${item.room_id})`;
        if (item.status) bedInfo += ` • Status: ${item.status}`;
        if (item.bed_type) bedInfo += ` • Type: ${item.bed_type}`;
        return bedInfo;
      }
      // Generic object formatting
      const keys = Object.keys(item);
      if (keys.length > 0) {
        // Try to find a meaningful display field
        const nameField = keys.find(k => k.includes('name') || k.includes('title'));
        const idField = keys.find(k => k.includes('id') || k.includes('number'));
        
        if (nameField) {
          let result = `${item[nameField]}`;
          if (idField && item[idField]) result += ` (${item[idField]})`;
          return result;
        } else if (idField) {
          return `ID: ${item[idField]}`;
        } else {
          // Show first few key-value pairs
          return keys.slice(0, 2).map(k => `${k}: ${item[k]}`).join(', ');
        }
      }
    }
    
    return String(item);
  };

  /**
   * Disconnect from MCP server
   */
  const disconnect = async () => {
    if (aiMcpServiceRef.current) {
      await aiMcpServiceRef.current.disconnect();
    }
    setIsConnected(false);
    setShowSetup(true);
    setServerInfo(null);
    setMessages([]);
  };

  /**
   * Check server status
   */
  const checkStatus = async () => {
    if (aiMcpServiceRef.current) {
      try {
        const status = await aiMcpServiceRef.current.checkStatus();
        setServerInfo(status);
        
        if (status && !status.isConnected) {
          setIsConnected(false);
          setMessages(prev => [...prev, {
            id: Date.now(),
            text: '🔌 MCP server connection lost. Please reconnect.',
            sender: 'ai',
            timestamp: new Date().toLocaleTimeString()
          }]);
        }
      } catch (error) {
        console.error('Status check failed:', error);
      }
    }
  };

  /**
   * Search for patient by patient number and get UUID
   */
  const searchPatientByNumber = async (patientNumber) => {
    if (!patientNumber.trim()) {
      return null;
    }

    setSearchingPatient(true);
    try {
      const response = await fetch('http://localhost:8000/tools/call', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          params: {
            name: 'search_patients',
            arguments: {
              patient_number: patientNumber.trim()
            }
          }
        })
      });

      const result = await response.json();
      
      if (result.result?.content?.[0]?.text) {
        const data = JSON.parse(result.result.content[0].text);
        
        if (data.success && data.result?.data?.length > 0) {
          const patient = data.result.data[0]; // Get first matching patient
          return {
            id: patient.id,
            patient_number: patient.patient_number,
            name: `${patient.first_name} ${patient.last_name}`,
            patient: patient
          };
        }
      }
      return null;
    } catch (error) {
      console.error('Patient search error:', error);
      return null;
    } finally {
      setSearchingPatient(false);
    }
  };

  /**
   * Handle patient number verification
   */
  const verifyPatient = async () => {
    if (!selectedPatientNumber.trim()) return;

    const patient = await searchPatientByNumber(selectedPatientNumber);
    
    if (patient) {
      setSelectedPatientId(patient.id);
      setPatientSearchResult(patient);
    } else {
      setPatientSearchResult(null);
      setSelectedPatientId(null);
      // Show error message
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: `❌ No patient found with number: ${selectedPatientNumber}. Please check the patient number or create a new patient.`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      }]);
    }
  };

  /**
   * Handle patient admission form input changes
   */
  const handleAdmissionFormChange = (field, value) => {
    setAdmissionFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  /**
   * Submit patient admission form
   */
  const submitPatientAdmission = async () => {
    // Validate required fields
    const requiredFields = ['first_name', 'last_name', 'date_of_birth'];
    const missingFields = requiredFields.filter(field => !admissionFormData[field].trim());
    
    if (missingFields.length > 0) {
      alert(`Please fill in the following required fields: ${missingFields.join(', ')}`);
      return;
    }

    setIsSubmittingAdmission(true);

    try {
      // Call the MCP tool directly to create the patient (bypass AI processing)
      const response = await aiMcpServiceRef.current.callToolDirectly('create_patient', {
        first_name: admissionFormData.first_name,
        last_name: admissionFormData.last_name,
        date_of_birth: admissionFormData.date_of_birth,
        gender: admissionFormData.gender,
        phone: admissionFormData.phone,
        email: admissionFormData.email,
        address: admissionFormData.address,
        emergency_contact_name: admissionFormData.emergency_contact_name,
        emergency_contact_phone: admissionFormData.emergency_contact_phone,
        blood_type: admissionFormData.blood_type,
        allergies: admissionFormData.allergies,
        medical_history: admissionFormData.medical_history
      });

      // Debug logging for deployment troubleshooting
      console.log('Patient admission response:', JSON.stringify(response, null, 2));

      // Close the form and show success message
      setShowPatientAdmissionForm(false);
      
      // Reset form data
      setAdmissionFormData({
        first_name: '',
        last_name: '',
        date_of_birth: '',
        gender: '',
        phone: '',
        email: '',
        address: '',
        emergency_contact_name: '',
        emergency_contact_phone: '',
        blood_type: '',
        allergies: '',
        medical_history: ''
      });

      // Add success message to chat
      let responseText = '';
      if (response.success) {
        // Success case - handle nested response structure
        const patientData = response.result?.data || response.data || {};
        responseText = `✅ Patient created successfully in the database!
        
**Patient Details:**
- Name: ${patientData.first_name || 'Unknown'} ${patientData.last_name || 'Unknown'}
- Patient Number: ${patientData.patient_number || patientData.id || 'Not generated'}
- Date of Birth: ${patientData.date_of_birth || 'Not provided'}
- Gender: ${patientData.gender || 'Not specified'}
- Phone: ${patientData.phone || 'Not provided'}
- Email: ${patientData.email || 'Not provided'}`;
      } else {
        // Error case
        responseText = `❌ Failed to create patient: ${response.message || 'Unknown error'}`;
      }

      const successMsg = {
        id: Date.now(),
        text: `✅ Patient admission completed successfully!\n\n${responseText}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, successMsg]);

    } catch (error) {
      console.error('Error submitting patient admission:', error);
      
      // Add error message to chat
      const errorMsg = {
        id: Date.now(),
        text: `❌ Error during patient admission: ${error.message || 'Unknown error occurred'}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsSubmittingAdmission(false);
    }
  };

  /**
   * Close patient admission form
   */
  const closePatientAdmissionForm = () => {
    setShowPatientAdmissionForm(false);
    
    // Add message indicating form was closed
    const cancelMsg = {
      id: Date.now(),
      text: "Patient admission form was closed. You can say 'admit patient' anytime to open it again.",
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, cancelMsg]);
  };

  // Department Form Handlers
  const handleDepartmentFormChange = (field, value) => {
    setDepartmentFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const submitDepartment = async () => {
    const requiredFields = ['name'];
    const missingFields = requiredFields.filter(field => !departmentFormData[field].trim());
    
    if (missingFields.length > 0) {
      alert(`Please fill in the following required fields: ${missingFields.join(', ')}`);
      return;
    }

    setIsSubmittingDepartment(true);

    try {
      const response = await aiMcpServiceRef.current.callToolDirectly('create_department', {
        name: departmentFormData.name,
        description: departmentFormData.description,
        head_doctor_id: departmentFormData.head_doctor_id,
        floor_number: departmentFormData.floor_number ? parseInt(departmentFormData.floor_number) : undefined,
        phone: departmentFormData.phone,
        email: departmentFormData.email
      });

      setShowDepartmentForm(false);
      setDepartmentFormData({
        name: '',
        description: '',
        head_doctor_id: '',
        floor_number: '',
        phone: '',
        email: ''
      });

      let responseText = '';
      if (response.success) {
        const deptData = response.result?.data || response.data || {};
        responseText = `✅ Department created successfully!
        
**Department Details:**
- Name: ${deptData.name || 'Unknown'}
- Description: ${deptData.description || 'Not provided'}
- Floor: ${deptData.floor_number || 'Not specified'}
- Phone: ${deptData.phone || 'Not provided'}
- Email: ${deptData.email || 'Not provided'}`;
      } else {
        responseText = `❌ Failed to create department: ${response.message || 'Unknown error'}`;
      }

      const successMsg = {
        id: Date.now(),
        text: `✅ Department created successfully!\n\n${responseText}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, successMsg]);

    } catch (error) {
      console.error('Error creating department:', error);
      
      const errorMsg = {
        id: Date.now(),
        text: `❌ Error creating department: ${error.message || 'Unknown error occurred'}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsSubmittingDepartment(false);
    }
  };

  const closeDepartmentForm = () => {
    setShowDepartmentForm(false);
    const cancelMsg = {
      id: Date.now(),
      text: "Department creation form was closed. You can say 'create department' anytime to open it again.",
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, cancelMsg]);
  };

  // Staff Form Handlers
  const handleStaffFormChange = (field, value) => {
    setStaffFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const submitStaff = async () => {
    const requiredFields = ['user_id', 'employee_id', 'position', 'department_id'];
    const missingFields = requiredFields.filter(field => !staffFormData[field].trim());
    
    if (missingFields.length > 0) {
      alert(`Please fill in the following required fields: ${missingFields.join(', ')}`);
      return;
    }

    setIsSubmittingStaff(true);

    try {
      const response = await aiMcpServiceRef.current.callToolDirectly('create_staff', {
        user_id: staffFormData.user_id,
        employee_id: staffFormData.employee_id,
        department_id: staffFormData.department_id,
        position: staffFormData.position,
        specialization: staffFormData.specialization,
        license_number: staffFormData.license_number,
        hire_date: staffFormData.hire_date,
        salary: staffFormData.salary ? parseFloat(staffFormData.salary) : undefined,
        shift_pattern: staffFormData.shift_pattern,
        status: staffFormData.status
      });

      setShowStaffForm(false);
      setStaffFormData({
        user_id: '',
        employee_id: '',
        department_id: '',
        position: '',
        specialization: '',
        license_number: '',
        hire_date: '',
        salary: '',
        shift_pattern: '',
        status: 'active'
      });

      let responseText = '';
      if (response.success) {
        const staffData = response.result?.data || response.data || {};
        responseText = `✅ Staff member created successfully!
        
**Staff Details:**
- Employee ID: ${staffData.employee_id || 'Not provided'}
- Position: ${staffData.position || 'Not provided'}
- Department ID: ${staffData.department_id || 'Not provided'}
- Status: ${staffData.status || 'Active'}`;
      } else {
        responseText = `❌ Failed to create staff member: ${response.message || 'Unknown error'}`;
      }

      const successMsg = {
        id: Date.now(),
        text: `✅ Staff member created successfully!\n\n${responseText}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, successMsg]);

    } catch (error) {
      console.error('Error creating staff:', error);
      
      const errorMsg = {
        id: Date.now(),
        text: `❌ Error creating staff: ${error.message || 'Unknown error occurred'}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsSubmittingStaff(false);
    }
  };

  const closeStaffForm = () => {
    setShowStaffForm(false);
    const cancelMsg = {
      id: Date.now(),
      text: "Staff creation form was closed. You can say 'create staff' anytime to open it again.",
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, cancelMsg]);
  };

  // User Form Handlers
  const handleUserFormChange = (field, value) => {
    setUserFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const submitUser = async () => {
    const requiredFields = ['username', 'email', 'password_hash', 'role', 'first_name', 'last_name'];
    const missingFields = requiredFields.filter(field => !userFormData[field] || userFormData[field].toString().trim() === '');
    
    if (missingFields.length > 0) {
      alert(`Please fill in the following required fields: ${missingFields.join(', ')}`);
      return;
    }

    setIsSubmittingUser(true);

    try {
      const response = await aiMcpServiceRef.current.callToolDirectly('create_user', {
        username: userFormData.username,
        email: userFormData.email,
        password_hash: userFormData.password_hash,
        role: userFormData.role,
        first_name: userFormData.first_name,
        last_name: userFormData.last_name,
        phone: userFormData.phone,
        is_active: userFormData.is_active
      });

      setShowUserForm(false);
      setUserFormData({
        username: '',
        email: '',
        password_hash: '',
        role: '',
        first_name: '',
        last_name: '',
        phone: '',
        is_active: true
      });

      let responseText = '';
      if (response.success) {
        const userData = response.result?.data || response.data || {};
        responseText = `✅ User created successfully!
        
**User Details:**
- Username: ${userData.username || 'Unknown'}
- Email: ${userData.email || 'Unknown'}
- Role: ${userData.role || 'Unknown'}
- Name: ${userData.first_name || 'Unknown'} ${userData.last_name || 'Unknown'}
- Active: ${userData.is_active ? 'Yes' : 'No'}`;
      } else {
        responseText = `❌ Failed to create user: ${response.message || 'Unknown error'}`;
      }

      const successMsg = {
        id: Date.now(),
        text: `✅ User created successfully!\n\n${responseText}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, successMsg]);

    } catch (error) {
      console.error('Error creating user:', error);
      
      const errorMsg = {
        id: Date.now(),
        text: `❌ Error creating user: ${error.message || 'Unknown error occurred'}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsSubmittingUser(false);
    }
  };

  const closeUserForm = () => {
    setShowUserForm(false);
    const cancelMsg = {
      id: Date.now(),
      text: "User creation form was closed. You can say 'create user' anytime to open it again.",
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, cancelMsg]);
  };

  // Room Form Handlers
  const handleRoomFormChange = (field, value) => {
    setRoomFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const submitRoom = async () => {
    const requiredFields = ['room_number', 'department_id'];
    const missingFields = requiredFields.filter(field => !roomFormData[field].trim());
    
    if (missingFields.length > 0) {
      alert(`Please fill in the following required fields: ${missingFields.join(', ')}`);
      return;
    }

    setIsSubmittingRoom(true);

    try {
      const response = await aiMcpServiceRef.current.callToolDirectly('create_room', {
        room_number: roomFormData.room_number,
        department_id: roomFormData.department_id,
        room_type: roomFormData.room_type,
        floor_number: roomFormData.floor_number ? parseInt(roomFormData.floor_number) : undefined,
        capacity: roomFormData.capacity ? parseInt(roomFormData.capacity) : undefined
      });

      setShowRoomForm(false);
      setRoomFormData({
        room_number: '',
        room_type: '',
        capacity: '',
        floor_number: '',
        department_id: '',
        status: 'available'
      });

      let responseText = '';
      if (response.success) {
        const roomData = response.result?.data || response.data || {};
        responseText = `✅ Room created successfully!
        
**Room Details:**
- Room Number: ${roomData.room_number || 'Unknown'}
- Type: ${roomData.room_type || 'Standard'}
- Floor: ${roomData.floor_number || 'Not specified'}
- Capacity: ${roomData.capacity || 'Not specified'}
- Department ID: ${roomData.department_id || 'Not specified'}`;
      } else {
        responseText = `❌ Failed to create room: ${response.message || 'Unknown error'}`;
      }

      const successMsg = {
        id: Date.now(),
        text: `✅ Room created successfully!\n\n${responseText}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, successMsg]);

    } catch (error) {
      console.error('Error creating room:', error);
      
      const errorMsg = {
        id: Date.now(),
        text: `❌ Error creating room: ${error.message || 'Unknown error occurred'}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsSubmittingRoom(false);
    }
  };

  const closeRoomForm = () => {
    setShowRoomForm(false);
    const cancelMsg = {
      id: Date.now(),
      text: "Room creation form was closed. You can say 'create room' anytime to open it again.",
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, cancelMsg]);
  };

  // Bed Form Handlers
  const handleBedFormChange = (field, value) => {
    setBedFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const submitBed = async () => {
    const requiredFields = ['bed_number'];
    const missingFields = requiredFields.filter(field => !bedFormData[field].trim());
    
    if (missingFields.length > 0) {
      alert(`Please fill in the following required fields: ${missingFields.join(', ')}`);
      return;
    }

    setIsSubmittingBed(true);

    try {
      const response = await aiMcpServiceRef.current.callToolDirectly('create_bed', {
        bed_number: bedFormData.bed_number,
        room_id: bedFormData.room_id,
        bed_type: bedFormData.bed_type,
        status: bedFormData.status
      });

      setShowBedForm(false);
      setBedFormData({
        bed_number: '',
        room_id: '',
        bed_type: '',
        status: 'available'
      });

      let responseText = '';
      if (response.success) {
        const bedData = response.result?.data || response.data || {};
        responseText = `✅ Bed created successfully!
        
**Bed Details:**
- Bed Number: ${bedData.bed_number || 'Unknown'}
- Room ID: ${bedData.room_id || 'Unknown'}
- Type: ${bedData.bed_type || 'Standard'}
- Status: ${bedData.status || 'Available'}`;
      } else {
        responseText = `❌ Failed to create bed: ${response.message || 'Unknown error'}`;
      }

      const successMsg = {
        id: Date.now(),
        text: `✅ Bed created successfully!\n\n${responseText}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, successMsg]);

    } catch (error) {
      console.error('Error creating bed:', error);
      
      const errorMsg = {
        id: Date.now(),
        text: `❌ Error creating bed: ${error.message || 'Unknown error occurred'}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsSubmittingBed(false);
    }
  };

  const closeBedForm = () => {
    setShowBedForm(false);
    const cancelMsg = {
      id: Date.now(),
      text: "Bed creation form was closed. You can say 'create bed' anytime to open it again.",
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, cancelMsg]);
  };

  // Equipment Form Handlers
  const handleEquipmentFormChange = (field, value) => {
    setEquipmentFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const submitEquipment = async () => {
    const requiredFields = ['equipment_id', 'name', 'category_id'];
    const missingFields = requiredFields.filter(field => !equipmentFormData[field].trim());
    
    if (missingFields.length > 0) {
      alert(`Please fill in the following required fields: ${missingFields.join(', ')}`);
      return;
    }

    setIsSubmittingEquipment(true);

    try {
      const response = await aiMcpServiceRef.current.callToolDirectly('create_equipment', {
        equipment_id: equipmentFormData.equipment_id,
        name: equipmentFormData.name,
        category_id: equipmentFormData.category_id,
        model: equipmentFormData.model,
        manufacturer: equipmentFormData.manufacturer,
        serial_number: equipmentFormData.serial_number,
        purchase_date: equipmentFormData.purchase_date,
        warranty_expiry: equipmentFormData.warranty_expiry,
        location: equipmentFormData.location,
        department_id: equipmentFormData.department_id,
        status: equipmentFormData.status,
        last_maintenance: equipmentFormData.last_maintenance,
        next_maintenance: equipmentFormData.next_maintenance,
        cost: equipmentFormData.cost ? parseFloat(equipmentFormData.cost) : undefined,
        notes: equipmentFormData.notes
      });

      setShowEquipmentForm(false);
      setEquipmentFormData({
        equipment_id: '',
        name: '',
        category_id: '',
        model: '',
        manufacturer: '',
        serial_number: '',
        purchase_date: '',
        warranty_expiry: '',
        location: '',
        department_id: '',
        status: 'available',
        cost: '',
        notes: ''
      });

      let responseText = '';
      if (response.success) {
        const equipmentData = response.result?.data || response.data || {};
        responseText = `✅ Equipment created successfully!
        
**Equipment Details:**
- Equipment ID: ${equipmentData.equipment_id}
- Name: ${equipmentData.name}
- Model: ${equipmentData.model || 'Not specified'}
- Location: ${equipmentData.location || 'Not specified'}
- Status: ${equipmentData.status}`;
      } else {
        responseText = `❌ Failed to create equipment: ${response.message || 'Unknown error'}`;
      }

      const successMsg = {
        id: Date.now(),
        text: `✅ Equipment created successfully!\n\n${responseText}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, successMsg]);

    } catch (error) {
      console.error('Error creating equipment:', error);
      
      const errorMsg = {
        id: Date.now(),
        text: `❌ Error creating equipment: ${error.message || 'Unknown error occurred'}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsSubmittingEquipment(false);
    }
  };

  const closeEquipmentForm = () => {
    setShowEquipmentForm(false);
    const cancelMsg = {
      id: Date.now(),
      text: "Equipment creation form was closed. You can say 'create equipment' anytime to open it again.",
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, cancelMsg]);
  };

  // Supply Form Handlers
  const handleSupplyFormChange = (field, value) => {
    setSupplyFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const submitSupply = async () => {
    const requiredFields = ['item_code', 'name', 'category_id', 'unit_of_measure'];
    const missingFields = requiredFields.filter(field => !supplyFormData[field].trim());
    
    if (missingFields.length > 0) {
      alert(`Please fill in the following required fields: ${missingFields.join(', ')}`);
      return;
    }

    setIsSubmittingSupply(true);

    try {
      const response = await aiMcpServiceRef.current.callToolDirectly('create_supply', {
        item_code: supplyFormData.item_code,
        name: supplyFormData.name,
        category_id: supplyFormData.category_id,
        description: supplyFormData.description,
        unit_of_measure: supplyFormData.unit_of_measure,
        minimum_stock_level: supplyFormData.minimum_stock_level ? parseInt(supplyFormData.minimum_stock_level) : undefined,
        maximum_stock_level: supplyFormData.maximum_stock_level ? parseInt(supplyFormData.maximum_stock_level) : undefined,
        current_stock: supplyFormData.current_stock ? parseInt(supplyFormData.current_stock) : undefined,
        unit_cost: supplyFormData.unit_cost ? parseFloat(supplyFormData.unit_cost) : undefined,
        supplier: supplyFormData.supplier,
        expiry_date: supplyFormData.expiry_date,
        location: supplyFormData.location
      });

      setShowSupplyForm(false);
      setSupplyFormData({
        item_code: '',
        name: '',
        category_id: '',
        description: '',
        unit_of_measure: '',
        minimum_stock_level: '',
        maximum_stock_level: '',
        current_stock: '',
        unit_cost: '',
        supplier: '',
        expiry_date: '',
        location: ''
      });

      let responseText = '';
      if (response.success) {
        const supplyData = response.result?.data || response.data || {};
        responseText = `✅ Supply created successfully!
        
**Supply Details:**
- Item Code: ${supplyData.item_code}
- Name: ${supplyData.name}
- Current Stock: ${supplyData.current_stock || '0'}
- Unit: ${supplyData.unit_of_measure}
- Location: ${supplyData.location || 'Not specified'}`;
      } else {
        responseText = `❌ Failed to create supply: ${response.message || 'Unknown error'}`;
      }

      const successMsg = {
        id: Date.now(),
        text: `✅ Supply created successfully!\n\n${responseText}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, successMsg]);

    } catch (error) {
      console.error('Error creating supply:', error);
      
      const errorMsg = {
        id: Date.now(),
        text: `❌ Error creating supply: ${error.message || 'Unknown error occurred'}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsSubmittingSupply(false);
    }
  };

  const closeSupplyForm = () => {
    setShowSupplyForm(false);
    const cancelMsg = {
      id: Date.now(),
      text: "Supply creation form was closed. You can say 'create supply' anytime to open it again.",
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, cancelMsg]);
  };

  // Legacy User Form Handlers
  const handleLegacyUserFormChange = (field, value) => {
    setLegacyUserFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const submitLegacyUser = async () => {
    const requiredFields = ['name', 'email'];
    const missingFields = requiredFields.filter(field => !legacyUserFormData[field].trim());
    
    if (missingFields.length > 0) {
      alert(`Please fill in the following required fields: ${missingFields.join(', ')}`);
      return;
    }

    setIsSubmittingLegacyUser(true);

    try {
      const response = await aiMcpServiceRef.current.callToolDirectly('create_legacy_user', {
        name: legacyUserFormData.name,
        email: legacyUserFormData.email,
        address: legacyUserFormData.address,
        phone: legacyUserFormData.phone
      });

      setShowLegacyUserForm(false);
      setLegacyUserFormData({
        name: '',
        email: '',
        role: ''
      });

      let responseText = '';
      if (response.success) {
        const legacyUserData = response.result?.data || response.data || {};
        responseText = `✅ Legacy user created successfully!
        
**Legacy User Details:**
- Name: ${legacyUserData.name}
- Email: ${legacyUserData.email}
- Phone: ${legacyUserData.phone || 'Not provided'}
- Address: ${legacyUserData.address || 'Not provided'}`;
      } else {
        responseText = `❌ Failed to create legacy user: ${response.message || 'Unknown error'}`;
      }

      const successMsg = {
        id: Date.now(),
        text: `✅ Legacy user created successfully!\n\n${responseText}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, successMsg]);

    } catch (error) {
      console.error('Error creating legacy user:', error);
      
      const errorMsg = {
        id: Date.now(),
        text: `❌ Error creating legacy user: ${error.message || 'Unknown error occurred'}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsSubmittingLegacyUser(false);
    }
  };

  const closeLegacyUserForm = () => {
    setShowLegacyUserForm(false);
    const cancelMsg = {
      id: Date.now(),
      text: "Legacy user creation form was closed. You can say 'create legacy user' anytime to open it again.",
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, cancelMsg]);
  };

  // Equipment Category Form Handlers
  const handleEquipmentCategoryFormChange = (field, value) => {
    setEquipmentCategoryFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const submitEquipmentCategory = async () => {
    const requiredFields = ['name'];
    const missingFields = requiredFields.filter(field => !equipmentCategoryFormData[field].trim());
    
    if (missingFields.length > 0) {
      alert(`Please fill in the following required fields: ${missingFields.join(', ')}`);
      return;
    }

    setIsSubmittingEquipmentCategory(true);

    try {
      const response = await aiMcpServiceRef.current.callToolDirectly(
        'create_equipment_category',
        equipmentCategoryFormData
      );

      let responseText = '';
      if (response && response.success) {
        responseText = `✅ Equipment category "${equipmentCategoryFormData.name}" created successfully!`;
        setEquipmentCategoryFormData({ name: '', description: '' });
        setShowEquipmentCategoryForm(false);
        // Reload equipment categories for dropdowns
        await loadDropdownOptions();
      } else {
        responseText = `❌ Failed to create equipment category: ${response.message || 'Unknown error'}`;
      }

      const responseMsg = {
        id: Date.now(),
        text: responseText,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, responseMsg]);

    } catch (error) {
      const errorMsg = {
        id: Date.now(),
        text: `❌ Error creating equipment category: ${error.message}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsSubmittingEquipmentCategory(false);
    }
  };

  const closeEquipmentCategoryForm = () => {
    setShowEquipmentCategoryForm(false);
    const cancelMsg = {
      id: Date.now(),
      text: "Equipment category creation form was closed. You can say 'create equipment category' anytime to open it again.",
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, cancelMsg]);
  };

  // Supply Category Form Handlers
  const handleSupplyCategoryFormChange = (field, value) => {
    setSupplyCategoryFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const submitSupplyCategory = async () => {
    const requiredFields = ['name'];
    const missingFields = requiredFields.filter(field => !supplyCategoryFormData[field].trim());
    
    if (missingFields.length > 0) {
      alert(`Please fill in the following required fields: ${missingFields.join(', ')}`);
      return;
    }

    setIsSubmittingSupplyCategory(true);

    try {
      const response = await aiMcpServiceRef.current.callToolDirectly(
        'create_supply_category',
        supplyCategoryFormData
      );

      let responseText = '';
      if (response && response.success) {
        responseText = `✅ Supply category "${supplyCategoryFormData.name}" created successfully!`;
        setSupplyCategoryFormData({ name: '', description: '' });
        setShowSupplyCategoryForm(false);
        // Reload supply categories for dropdowns
        await loadDropdownOptions();
      } else {
        responseText = `❌ Failed to create supply category: ${response.message || 'Unknown error'}`;
      }

      const responseMsg = {
        id: Date.now(),
        text: responseText,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, responseMsg]);

    } catch (error) {
      const errorMsg = {
        id: Date.now(),
        text: `❌ Error creating supply category: ${error.message}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsSubmittingSupplyCategory(false);
    }
  };

  const closeSupplyCategoryForm = () => {
    setShowSupplyCategoryForm(false);
    const cancelMsg = {
      id: Date.now(),
      text: "Supply category creation form was closed. You can say 'create supply category' anytime to open it again.",
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, cancelMsg]);
  };

  // Setup Panel - Dark Chatbot Style
  if (showSetup) {
    return (
      <div className="h-screen bg-[#1a1a1a] flex flex-col text-white">
        {/* Header */}
        <div className="border-b border-gray-700 px-4 py-3 bg-[#1a1a1a]">
          <div className="flex items-center space-x-3">
            <div className="w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium shadow-lg">
              H
            </div>
            <div>
              <h1 className="text-sm font-medium text-white">Hospital Assistant</h1>
              <p className="text-xs text-gray-400">Setup & Configuration</p>
            </div>
          </div>
        </div>

        {/* Main Setup Content */}
        <div className="flex-1 overflow-y-auto bg-[#1a1a1a] flex items-center justify-center">
          <div className="max-w-lg w-full mx-4">
            {/* Welcome Section */}
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
                <span className="text-2xl font-medium text-white">H</span>
              </div>
              <h1 className="text-2xl font-medium text-white mb-3">
                Welcome to Hospital Assistant
              </h1>
              <p className="text-gray-400 mb-6 text-sm">
                Connect to your hospital management system to get started with AI-powered healthcare administration.
              </p>
            </div>

            {/* Configuration Form */}
            <div className="space-y-6">
              {/* API Key Section */}
              <div className="bg-[#2a2a2a] rounded-lg p-6 border border-gray-700">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-white font-medium">OpenAI API Key</h3>
                    <p className="text-xs text-gray-400">Required for AI conversation processing</p>
                  </div>
                </div>
                <input
                  type="password"
                  value={openaiApiKey}
                  onChange={(e) => setOpenaiApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full px-4 py-3 bg-[#1a1a1a] border border-gray-600 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-white placeholder-gray-400 text-sm"
                />
              </div>

              {/* Server Status */}
              <div className="bg-[#2a2a2a] rounded-lg p-4 border border-gray-700">
                <h4 className="text-white font-medium mb-2 text-sm">📡 Server Connection</h4>
                <p className="text-xs text-gray-400">
                  Connecting directly to FastMCP server at: <br/>
                  <code className="text-green-400">http://127.0.0.1:8000</code>
                </p>
              </div>

              {/* Connection Status */}
              {connectionError && (
                <div className={`p-4 rounded-lg text-sm border ${
                  connectionError.includes('✅') 
                    ? 'bg-green-900/20 text-green-400 border-green-800' 
                    : 'bg-red-900/20 text-red-400 border-red-800'
                }`}>
                  {connectionError}
                </div>
              )}

              {/* Action Buttons */}
              <div className="space-y-3">
                <button
                  onClick={async () => {
                    setConnectionError('');
                    try {
                      const response = await fetch('http://127.0.0.1:8000/');
                      if (response.ok) {
                        setConnectionError('✅ FastMCP Server is running and ready');
                      } else {
                        setConnectionError(`❌ Server error: ${response.status}`);
                      }
                    } catch (error) {
                      setConnectionError(`❌ Cannot reach FastMCP Server: ${error.message}\nMake sure comprehensive_server.py is running on port 8000`);
                    }
                  }}
                  className="w-full py-3 px-4 bg-[#333] hover:bg-[#404040] text-white rounded-lg transition-colors text-sm font-medium border border-gray-600"
                >
                  <div className="flex items-center justify-center space-x-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>Test Server Connection</span>
                  </div>
                </button>
                
                <button
                  onClick={initializeService}
                  disabled={isLoading || !openaiApiKey.trim()}
                  className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-all duration-200 font-medium"
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Connecting to Hospital System...</span>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center space-x-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      <span>Connect to Hospital System</span>
                    </div>
                  )}
                </button>
              </div>

              {/* Quick Tips */}
              <div className="bg-[#2a2a2a] rounded-lg p-4 border border-gray-700">
                <h4 className="text-white font-medium mb-2 text-sm">Quick Tips:</h4>
                <ul className="text-xs text-gray-400 space-y-1">
                  <li>• Make sure comprehensive_server.py is running on port 8000</li>
                  <li>• Your OpenAI API key needs GPT-4 access for best results</li>
                  <li>• No process manager needed - direct HTTP connection</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Main Chat Interface - Claude Desktop Style with Responsive Design
  return (
    <div className="bg-[#1a1a1a] flex flex-col text-white overflow-hidden relative" style={{ height: 'calc(var(--vh, 1vh) * 100)' }}>
      {/* Claude-style Header - FIXED AT TOP */}
      <div className="fixed top-0 left-0 right-0 border-b border-gray-700 px-3 sm:px-4 py-3 bg-[#1a1a1a] z-30">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 sm:space-x-3">
            <div className="w-6 h-6 sm:w-7 sm:h-7 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs sm:text-sm font-medium shadow-lg">
              H
            </div>
            <div className="min-w-0 flex-1">
              <h1 className="text-sm font-medium text-white truncate">Hospital Agent</h1>
              {serverInfo && (
                <p className="text-xs text-gray-400 hidden sm:block">
                  Connected • {serverInfo.toolCount} tools • {aiMcpServiceRef.current?.getConversationSummary?.()?.messageCount || 0} messages in memory
                </p>
              )}
            </div>
          </div>
          
          {/* User Info and Actions - Responsive */}
          <div className="flex items-center space-x-1 sm:space-x-3">
            {/* User Profile */}
            <div className="flex items-center space-x-1 sm:space-x-2">
              <div className="w-5 h-5 sm:w-6 sm:h-6 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-medium">
                  {user?.fullName ? user.fullName.charAt(0).toUpperCase() : user?.email?.charAt(0).toUpperCase() || 'U'}
                </span>
              </div>
              <div className="hidden md:block">
                <p className="text-xs text-white font-medium">{user?.fullName || 'User'}</p>
                <p className="text-xs text-gray-400">{user?.role || 'Staff'}</p>
              </div>
            </div>

            {/* Action Buttons - Responsive with Mobile Menu */}
            <div className="flex items-center space-x-1">
              {/* Mobile: Show only essential buttons */}
              <div className="flex items-center space-x-1 sm:hidden">
                {/* <button
                  onClick={() => setShowSetup(true)}
                  className="p-1.5 text-gray-400 hover:text-gray-300 hover:bg-gray-700 rounded-md transition-colors"
                  title="Settings"
                >
                  <Settings className="w-4 h-4" />
                </button> */}
                <button
                  onClick={onLogout}
                  className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded-md transition-colors"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
              
              {/* Desktop: Show all buttons */}
              <div className="hidden sm:flex items-center space-x-1">
                <button
                  onClick={() => {
                    if (aiMcpServiceRef.current) {
                      aiMcpServiceRef.current.resetConversation();
                      setMessages(prev => [...prev, {
                        id: Date.now(),
                        text: '🔄 **Conversation Reset** - Memory cleared. Starting fresh!',
                        sender: 'ai',
                        timestamp: new Date().toLocaleTimeString()
                      }]);
                    }
                  }}
                  className="p-1.5 text-gray-400 hover:text-gray-300 hover:bg-gray-700 rounded-md transition-colors"
                  title="Reset Conversation Memory"
                >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
              <button
                onClick={checkStatus}
                className="p-1.5 text-gray-400 hover:text-gray-300 hover:bg-gray-700 rounded-md transition-colors"
                title="Check Status"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </button>
              {/* <button
                onClick={disconnect}
                className="p-1.5 text-gray-400 hover:text-gray-300 hover:bg-gray-700 rounded-md transition-colors"
                title="Disconnect"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button> */}
              
              {/* Settings Button */}
              {/* <button
                onClick={() => setShowSetup(true)}
                className="p-1.5 text-gray-400 hover:text-gray-300 hover:bg-gray-700 rounded-md transition-colors"
                title="Settings"
              >
                <Settings className="w-4 h-4" />
              </button> */}
              
              {/* Logout Button */}
              <button
                onClick={onLogout}
                className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded-md transition-colors"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation - Hidden since we're using plus menu */}
      <div className="hidden border-b border-gray-700 bg-[#1a1a1a]">
        <div className="max-w-4xl mx-auto px-3 sm:px-4">
          <nav className="flex space-x-4 sm:space-x-8 overflow-x-auto">
            <button
              onClick={() => setActiveTab('chat')}
              className={`py-3 px-1 border-b-2 font-medium text-xs sm:text-sm flex items-center space-x-1 sm:space-x-2 whitespace-nowrap ${
                activeTab === 'chat'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              <User className="w-3 h-3 sm:w-4 sm:h-4" />
              <span className="hidden sm:inline">Chat Assistant</span>
              <span className="sm:hidden">Chat</span>
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className={`py-3 px-1 border-b-2 font-medium text-xs sm:text-sm flex items-center space-x-1 sm:space-x-2 whitespace-nowrap ${
                activeTab === 'upload'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              <Upload className="w-3 h-3 sm:w-4 sm:h-4" />
              <span className="hidden sm:inline">Upload Documents</span>
              <span className="sm:hidden">Upload</span>
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`py-3 px-1 border-b-2 font-medium text-xs sm:text-sm flex items-center space-x-1 sm:space-x-2 whitespace-nowrap ${
                activeTab === 'history'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              <History className="w-3 h-3 sm:w-4 sm:h-4" />
              <span className="hidden sm:inline">Medical History</span>
              <span className="sm:hidden">History</span>
            </button>
          </nav>
        </div>
      </div>

        {/* Fixed Back Button for Upload / History - ensures reliable navigation on mobile */}
        {(activeTab === 'upload' || activeTab === 'history') && (
          <div className="fixed left-4 top-[76px] z-40">
            <button
              onClick={() => setActiveTab('chat')}
              className="flex items-center space-x-2 bg-[#2a2a2a] hover:bg-[#333] text-white px-3 py-2 rounded-lg border border-gray-700 shadow-md"
              title="Back to Chat"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="hidden sm:inline">Back to Chat</span>
            </button>
          </div>
        )}

      {/* Content Area - MAIN SCROLLABLE CONTAINER */}
      {activeTab === 'chat' && (
        <div className="flex-1 flex flex-col min-h-0 overflow-hidden" style={{ 
          marginTop: '70px', 
          marginBottom: showActionButtons ? 'calc(150px + env(safe-area-inset-bottom, 0px))' : 'calc(120px + env(safe-area-inset-bottom, 0px))',
        }}>
          {/* Messages Container - ONLY THIS SCROLLS */}
          <div 
            ref={messagesContainerRef} 
            className="flex-1 overflow-y-auto overflow-x-hidden bg-[#1a1a1a] px-0 sm:px-2"
            style={{ 
              WebkitOverflowScrolling: 'touch',
              scrollBehavior: 'smooth'
            }}
            onClick={() => {
              // Smart focus input when clicking anywhere in the chat area, but not when selecting text
              const selection = window.getSelection();
              if (inputFieldRef.current && isConnected && selection.toString().length === 0) {
                if (isMobileDevice()) {
                  // On mobile: focus without keyboard popup
                  smartFocusInput(0);
                } else {
                  // On desktop: normal focus
                  inputFieldRef.current.focus();
                }
              }
            }}
          >
            <div className="max-w-4xl mx-auto px-3 sm:px-4">
              {messages.length === 0 && (
                <div className="flex items-center justify-center h-full text-center px-3 sm:px-6">
                  <div className="max-w-xs sm:max-w-md">
                    <div className="w-12 h-12 sm:w-16 sm:h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 sm:mb-6 shadow-lg">
                      <span className="text-lg sm:text-2xl font-medium text-white">H</span>
                    </div>
                    <h2 className="text-lg sm:text-xl font-medium text-white mb-2 sm:mb-3">
                      Welcome back, {user?.fullName?.split(' ')[0] || 'User'}!
                    </h2>
                    <p className="text-gray-400 mb-4 sm:mb-6 text-sm">
                      I'm your AI assistant for hospital management tasks. I can help you manage patients, staff, departments, equipment, and more through natural conversation.
                    </p>
                  </div>
                </div>
              )}
          
          {messages.map((message) => (
            <div key={message.id} className={`px-2 sm:px-4 py-2 ${
              message.isThinking ? 'bg-[#1a1a1a]' : 
              message.isFinalAnswer ? 'bg-[#1a1a1a]' : 
              message.isError ? 'bg-[#1a1a1a]' : 'bg-[#1a1a1a]'
            }`}>
              {message.sender === 'user' ? (
                // User message - aligned to the right - Responsive
                <div className="flex justify-end">
                  <div className="max-w-[85%] sm:max-w-[80%]">
                    <div className="prose prose-sm max-w-none">
                      <div className={`whitespace-pre-wrap leading-relaxed text-xs sm:text-sm text-white rounded-2xl px-3 sm:px-4 py-2 ${
                        message.isVoiceInput ? 'bg-blue-700 border border-blue-500' : 'bg-slate-700'
                      }`}>
                        {message.isVoiceInput && (
                          <div className="flex items-center space-x-1 mb-1 text-blue-200">
                            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                              <path d="M12 2c1.1 0 2 .9 2 2v6c0 1.1-.9 2-2 2s-2-.9-2-2V4c0-1.1.9-2 2-2zm5.3 6c0 3-2.5 5.1-5.3 5.1S6.7 11 6.7 8H5c0 3.4 2.7 6.2 6 6.7v3.3h2v-3.3c3.3-.5 6-3.3 6-6.7h-1.7z" />
                            </svg>
                            <span className="text-xs">Voice Input</span>
                          </div>
                        )}
                        <div dangerouslySetInnerHTML={{ __html: formatMessageText(message.text) }} />
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                // AI message - aligned to the left - Responsive
                <div className="flex space-x-2 sm:space-x-3">
                  <div className="w-6 h-6 sm:w-7 sm:h-7 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 text-xs sm:text-sm font-medium text-white shadow-lg">
                    {message.isThinking ? (
                      <div className="w-2 h-2 sm:w-3 sm:h-3 border border-gray-400 border-t-white rounded-full animate-spin"></div>
                    ) : (
                      'H'
                    )}
                  </div>
                
                <div className="flex-1 min-w-0">
                  {message.isThinking && (
                    <div className="mb-1">
                      <button
                        onClick={() => setExpandedThinking(prev => ({
                          ...prev,
                          [message.id]: !prev[message.id]
                        }))}
                        className="flex items-center space-x-1 sm:space-x-2 text-xs text-gray-500 italic hover:text-gray-400 transition-colors w-full justify-between"
                      >
                        <div className="flex items-center space-x-1 sm:space-x-2 min-w-0">
                          <span className="text-gray-400">🔧</span>
                          <span className="font-mono text-blue-400 truncate">{message.toolFunction || 'thinking'}</span>
                        </div>
                        <span className="ml-auto flex items-center space-x-1 flex-shrink-0">
                          <ThinkingDuration startTime={message.startTime} />
                          <svg 
                            className={`w-3 h-3 transform transition-transform ${expandedThinking[message.id] ? 'rotate-180' : ''}`} 
                            fill="none" 
                            stroke="currentColor" 
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </span>
                      </button>
                      {expandedThinking[message.id] && (
                        <div className="mt-2 text-xs sm:text-sm text-gray-300 pl-4 sm:pl-6">
                          {message.text}
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* Tool Call Display */}
                  {message.isToolCall && (
                    <div className="mb-2">
                      <div className="flex items-center space-x-2 text-xs text-gray-400 mb-1">
                        <span className="text-blue-400">🔧</span>
                        <span>Tool Execution</span>
                      </div>
                    </div>
                  )}
                  
                  <div className="prose prose-sm max-w-none">
                    {(!message.isThinking || expandedThinking[message.id]) && (
                      <div 
                        className={`whitespace-pre-wrap leading-relaxed text-sm ${
                          message.isThinking ? 'text-gray-300' :
                          message.isFinalAnswer ? 'text-white' :
                          message.isError ? 'text-red-400' :
                          message.isToolCall ? 'text-blue-200 bg-gray-800 p-3 rounded-lg border-l-2 border-blue-500' :
                          'text-white'
                        }`}
                        dangerouslySetInnerHTML={{
                          __html: formatMessageText(message.text)
                        }}
                      />
                    )}
                  </div>
                </div>
              </div>
              )}
            </div>
          ))}
          
          {isLoading && (
            <div className="px-4 py-2 bg-[#1a1a1a]">
              <div className="flex space-x-3">
                <div className="w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg">
                  <div className="w-3 h-3 border border-gray-400 border-t-white rounded-full animate-spin"></div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="mb-1">
                    <button
                      onClick={() => setExpandedThinking(prev => ({
                        ...prev,
                        ['loading']: !prev['loading']
                      }))}
                      className="flex items-center space-x-2 text-xs text-gray-500 italic hover:text-gray-400 transition-colors"
                    >
                      <span>Processing your request...</span>
                      <span className="ml-auto flex items-center space-x-1">
                        <span>0s</span>
                        <svg 
                          className={`w-3 h-3 transform transition-transform ${expandedThinking['loading'] ? 'rotate-180' : ''}`} 
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </span>
                    </button>
                  </div>
                  <div className="flex items-center space-x-2 text-gray-300 mb-1">
                    <span className="text-blue-400">🔍</span>
                    <span className="text-xs text-gray-400">Request Analysis</span>
                  </div>
                  {expandedThinking['loading'] && (
                    <div className="text-sm text-gray-300">
                      Analyzing your request and determining the best approach...
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Action Buttons Above Input - FIXED ABOVE BOTTOM INPUT */}
          <div className={`fixed left-0 right-0 bg-[#1a1a1a] px-4 z-20 border-t border-gray-700 transition-all duration-500 ease-in-out ${
            showActionButtons ? 'py-3 opacity-100' : 'py-0 opacity-0 -bottom-full'
          }`} style={{
            bottom: showActionButtons ? 'calc(90px + env(safe-area-inset-bottom, 0px))' : '-100px',
            minHeight: showActionButtons ? '120px' : '0px'
          }}>
            <div className="max-w-4xl mx-auto">
            {/* Desktop: 1 row 4 columns, Mobile: 2 rows 2 columns */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {/* View All Patients */}
              <button
                onClick={() => {
                  setInputMessage("List all patients");
                  smartFocusInput(100);
                }}
                className="flex items-center justify-center bg-[#2a2a2a] hover:bg-[#333] text-white rounded-md sm:rounded-lg px-2 py-2 transition-colors text-xs border border-gray-600 hover:border-gray-500"
                title="View all patients"
              >
                <span className="font-medium whitespace-nowrap">View Patients</span>
              </button>

              {/* Check Bed Status */}
              <button
                onClick={() => {
                  setInputMessage("Show bed availability");
                  smartFocusInput(100);
                }}
                className="flex items-center justify-center bg-[#2a2a2a] hover:bg-[#333] text-white rounded-md sm:rounded-lg px-2 py-2 transition-colors text-xs border border-gray-600 hover:border-gray-500"
                title="Check bed availability"
              >
                <span className="font-medium whitespace-nowrap">Bed Status</span>
              </button>

              {/* Emergency Alert */}
              <button
                onClick={() => {
                  setInputMessage("Show emergency status and available emergency beds");
                  smartFocusInput(100);
                }}
                className="flex items-center justify-center bg-[#2a2a2a] hover:bg-[#333] text-white rounded-md sm:rounded-lg px-2 py-2 transition-colors text-xs border border-gray-600 hover:border-gray-500"
                title="Emergency status"
              >
                <span className="font-medium whitespace-nowrap">Emergency</span>
              </button>

              {/* staff list */}
              <button
                onClick={() => {
                  setInputMessage("Show staff list");
                  smartFocusInput(100);
                }}
                className="flex items-center justify-center bg-[#2a2a2a] hover:bg-[#333] text-white rounded-md sm:rounded-lg px-2 py-2 transition-colors text-xs border border-gray-600 hover:border-gray-500"
                title="Staff List"
              >
                <span className="font-medium whitespace-nowrap">Staff List</span>
              </button>
            </div>
          </div>
        </div>

        {/* Modern Chat Input - FIXED AT BOTTOM */}
        <div 
          className="fixed bottom-0 left-0 right-0 bg-[#1a1a1a] px-3 sm:px-4 py-2 border-t border-gray-700 z-30"
          style={{ 
            paddingBottom: 'calc(8px + env(safe-area-inset-bottom, 0px))',
            position: 'fixed',
            willChange: 'transform',
            transform: isInputFocused && isMobileDevice() ? 'translateY(-10vh)' : 'translateY(0)',
            transition: 'transform 0.3s ease-out'
          }}
        >
          <div className="max-w-4xl mx-auto">
              {/* Voice Status Indicator */}
              {(isRecording || isProcessingVoice || isSpeaking) && (
                <div className="mb-3 px-3 py-2 bg-[#2a2a2a] border border-gray-600 rounded-lg">
                  <div className="flex items-center space-x-2">
                    {isRecording && (
                      <>
                        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                        <span className="text-sm text-red-400">
                          🎤 Recording with OpenAI Whisper...
                        </span>
                      </>
                    )}
                    {isProcessingVoice && (
                      <>
                        <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                        <span className="text-sm text-yellow-400">
                          🔄 Processing speech with OpenAI...
                        </span>
                      </>
                    )}
                    {isSpeaking && (
                      <>
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                        <span className="text-sm text-blue-400">
                          🔊 Speaking with OpenAI TTS...
                        </span>
                      </>
                    )}
                  </div>
                </div>
              )}
              
              <div className="relative">
                {/* Main Input Container - Rounded Rectangle */}
                <div className={`bg-[#2a2a2a] rounded-2xl sm:rounded-3xl border px-3 sm:px-4 py-3 sm:py-4 transition-colors duration-200 ${
                  isInputFocused ? 'border-blue-500' : 'border-gray-600'
                }`}>
                  
                  {/* First Row - Text Input (Full Width) */}
                  <div className="mb-2 sm:mb-3">
                    <textarea
                      ref={inputFieldRef}
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          handleSendMessage();
                        }
                      }}
                      onFocus={() => {
                        setIsInputFocused(true);
                        // Scroll to make input visible above keyboard on mobile
                        if (isMobileDevice()) {
                          // Small delay to let keyboard appear
                          setTimeout(() => {
                            // Scroll the input into view
                            inputFieldRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            
                            // Force additional scroll to ensure it's visible above keyboard
                            const scrollY = window.scrollY || window.pageYOffset;
                            window.scrollTo({
                              top: Math.max(0, scrollY - 150),
                              behavior: 'smooth'
                            });
                          }, 300);
                        }
                      }}
                      onBlur={() => setIsInputFocused(false)}
                      placeholder={isConnected ? "Ask anything (Ctrl+/ to focus)" : "Ask anything"}
                      disabled={!isConnected || isLoading}
                      rows={1}
                      className="w-full bg-transparent border-none outline-none resize-none text-white placeholder-gray-400 text-base"
                      style={{
                        minHeight: '20px',
                        maxHeight: '120px',
                        fontSize: '16px', // Prevents zoom on iOS
                        WebkitAppearance: 'none',
                        WebkitBorderRadius: 0
                      }}
                      onInput={(e) => {
                        e.target.style.height = 'auto';
                        e.target.style.height = e.target.scrollHeight + 'px';
                        
                        // On mobile, ensure the view adjusts as user types
                        if (isMobileDevice()) {
                          // Scroll input into view
                          inputFieldRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                          
                          // Also force move the entire input area above keyboard
                          setTimeout(() => {
                            // Additional upward scroll for safety
                            window.scrollTo({
                              top: Math.max(0, window.scrollY - 150),
                              behavior: 'smooth'
                            });
                          }, 100);
                        }
                      }}
                    />
                  </div>
                  
                  {/* Second Row - Icons */}
                  <div className="flex items-center justify-between">
                    {/* Left Side - Plus and Tools Icons */}
                    <div className="flex items-center space-x-2 sm:space-x-3">
                      {/* Plus Button with Dropdown */}
                      <div className="relative" ref={plusMenuRef}>
                        <button
                          onClick={() => setShowPlusMenu(!showPlusMenu)}
                          className="text-gray-400 hover:text-white transition-colors p-1"
                          title="Upload documents or view medical history"
                        >
                          <Plus className="w-4 h-4" />
                        </button>
                        
                        {showPlusMenu && (
                          <div className="absolute bottom-full left-0 mb-2 bg-[#2a2a2a] border border-gray-600 rounded-lg shadow-lg min-w-48 z-50">
                            <button
                              onClick={() => {
                                setActiveTab('upload');
                                setShowPlusMenu(false);
                              }}
                              className="w-full text-left px-3 py-2 text-sm text-white hover:bg-gray-700 rounded-t-lg flex items-center space-x-2"
                            >
                              <Upload className="w-4 h-4" />
                              <span>Upload Documents</span>
                            </button>
                            <button
                              onClick={() => {
                                setActiveTab('history');
                                setShowPlusMenu(false);
                              }}
                              className="w-full text-left px-3 py-2 text-sm text-white hover:bg-gray-700 rounded-b-lg border-t border-gray-600 flex items-center space-x-2"
                            >
                              <History className="w-4 h-4" />
                              <span>Medical History</span>
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {/* Right Side - Send Button */}
                    <div className="flex items-center">
                      {/* Microphone Button */}
                      <button
                        onClick={toggleVoiceInput}
                        disabled={!isConnected || isLoading || isProcessingVoice || microphoneAvailable === false}
                        className={`transition-colors duration-200 p-1 ${
                          microphoneAvailable === false
                            ? "text-gray-500 cursor-not-allowed opacity-50"
                            : isListening || isRecording
                            ? "text-red-400 hover:text-red-300 animate-pulse"
                            : isProcessingVoice
                            ? "text-yellow-400 hover:text-yellow-300 animate-pulse"
                            : isSpeaking
                            ? "text-blue-400 hover:text-blue-300 animate-pulse"
                            : "text-gray-400 hover:text-white disabled:text-gray-600"
                        }`}
                        title={
                          microphoneAvailable === false
                            ? "Microphone not available (requires HTTPS connection and permissions)"
                            : microphoneAvailable === null
                            ? "Checking microphone availability..."
                            : isListening || isRecording
                            ? "Recording... (Click to stop)"
                            : isProcessingVoice
                            ? "Processing voice input..."
                            : isSpeaking
                            ? "AI is speaking... (Click to stop)"
                            : "Start voice input (OpenAI Whisper)"
                        }
                      >
                        {microphoneAvailable === false ? (
                          <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M19 11h-1.7c0 .74-.16 1.43-.43 2.05l1.23 1.23c.56-.98.9-2.09.9-3.28zm-4.02.17c0-.06.02-.11.02-.17V4c0-1.66-1.34-3-3-3S9 2.34 9 4v.18l5.98 5.99zM4.27 3L3 4.27l6.01 6.01V11c0 1.66 1.33 3 2.99 3 .22 0 .44-.03.65-.08l1.66 1.66c-.71.33-1.5.52-2.31.52-2.76 0-5.3-2.1-5.3-5.1H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c.91-.13 1.77-.45 2.54-.9L19.73 21 21 19.73 4.27 3z"/>
                          </svg>
                        ) : isListening || isRecording ? (
                          <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M6 6h12v12H6z" />
                          </svg>
                        ) : isProcessingVoice ? (
                          <svg className="w-4 h-4 sm:w-5 sm:h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                        ) : isSpeaking ? (
                          <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z" />
                          </svg>
                        ) : (
                          <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2c1.1 0 2 .9 2 2v6c0 1.1-.9 2-2 2s-2-.9-2-2V4c0-1.1.9-2 2-2zm5.3 6c0 3-2.5 5.1-5.3 5.1S6.7 11 6.7 8H5c0 3.4 2.7 6.2 6 6.7v3.3h2v-3.3c3.3-.5 6-3.3 6-6.7h-1.7z" />
                          </svg>
                        )}
                      </button>
                      {/* Send Button - Circular */}
                      <button
                        onClick={handleSendMessage}
                        disabled={!isConnected || isLoading || !inputMessage.trim()}
                        className="w-7 h-7 sm:w-8 sm:h-8 bg-gray-600 hover:bg-gray-500 disabled:bg-gray-700 text-white rounded-full flex items-center justify-center transition-colors duration-200"
                        title="Send message"
                      >
                        {isLoading ? (
                          <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 border border-white border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                          <svg className="w-3.5 h-3.5 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                          </svg>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Upload Documents Tab */}
      {activeTab === 'upload' && (
  <div onTouchStart={handleTouchStart} onTouchMove={handleTouchMove} onTouchEnd={handleTouchEnd} className="flex-1 overflow-y-auto bg-[#1a1a1a] p-3 sm:p-6">
          <div className="max-w-4xl mx-auto">
            <div className="mb-4 sm:mb-6">
              {/* Back to Chat Button */}
              <button
                onClick={() => setActiveTab('chat')}
                className="mb-4 flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                <span>Back to Chat</span>
              </button>
              
              <h2 className="text-xl sm:text-2xl font-bold text-white mb-2">Upload Medical Documents</h2>
              <p className="text-sm sm:text-base text-gray-400">Upload patient medical documents for AI-powered analysis and history tracking.</p>
            </div>
            
            {/* Patient Selection */}
            <div className="mb-4 sm:mb-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Select Patient by Patient Number
              </label>
              <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4">
                <input
                  type="text"
                  placeholder="Enter Patient Number (e.g., P123456)"
                  value={selectedPatientNumber}
                  onChange={(e) => setSelectedPatientNumber(e.target.value.toUpperCase())}
                  className="flex-1 p-3 bg-[#2a2a2a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
                  onKeyPress={(e) => e.key === 'Enter' && verifyPatient()}
                />
                <button
                  onClick={verifyPatient}
                  disabled={searchingPatient || !selectedPatientNumber.trim()}
                  className="bg-blue-600 text-white px-4 sm:px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center text-sm sm:text-base whitespace-nowrap"
                >
                  {searchingPatient ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      Searching...
                    </>
                  ) : (
                    'Verify Patient'
                  )}
                </button>
              </div>
              
              {/* Patient Search Result */}
              {patientSearchResult && (
                <div className="mt-3 p-3 bg-green-900/20 border border-green-500/30 rounded-lg">
                  <div className="flex items-center text-green-400">
                    <CheckCircle className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                    <span className="font-medium text-sm sm:text-base">Patient Found:</span>
                  </div>
                  <div className="mt-1 text-xs sm:text-sm text-gray-300 space-y-1">
                    <p><strong>Name:</strong> {patientSearchResult.name}</p>
                    <p><strong>Patient Number:</strong> {patientSearchResult.patient_number}</p>
                    <p><strong>Email:</strong> {patientSearchResult.patient.email || 'Not provided'}</p>
                    <p><strong>Phone:</strong> {patientSearchResult.patient.phone || 'Not provided'}</p>
                  </div>
                </div>
              )}
              
              <p className="text-xs text-gray-500 mt-2">
                Enter the patient number (like P123456) to verify the patient exists before uploading documents.
              </p>
            </div>

            {/* Enhanced Document Upload Component */}
            {selectedPatientId && (
              <EnhancedMedicalDocumentUpload 
                patientId={selectedPatientId}
                onUploadComplete={(results) => {
                  console.log('Documents uploaded:', results);
                  // Show success message and potentially switch to history tab
                  setMessages(prev => [...prev, {
                    id: Date.now(),
                    type: 'assistant',
                    content: `✅ Successfully uploaded ${results.length} medical document(s) for patient ${patientSearchResult?.name} (${patientSearchResult?.patient_number}). ${results.map(r => `\n• ${r.fileName}: ${r.entitiesCount} entities extracted`).join('')}`,
                    timestamp: new Date()
                  }]);
                }}
              />
            )}

            {!selectedPatientId && (
              <div className="text-center text-gray-500 py-8 sm:py-12">
                <Upload className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-4" />
                <p className="text-base sm:text-lg font-medium">Enter a Patient Number to start uploading documents</p>
                <p className="text-xs sm:text-sm">Search for the patient by their patient number (like P123456) before uploading medical documents.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Medical History Tab */}
      {activeTab === 'history' && (
  <div onTouchStart={handleTouchStart} onTouchMove={handleTouchMove} onTouchEnd={handleTouchEnd} className="flex-1 overflow-y-auto bg-[#1a1a1a] p-3 sm:p-6">
          <div className="max-w-4xl mx-auto">
            <div className="mb-4 sm:mb-6">
              {/* Back to Chat Button */}
              <button
                onClick={() => setActiveTab('chat')}
                className="mb-4 flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                <span>Back to Chat</span>
              </button>
              
              <h2 className="text-xl sm:text-2xl font-bold text-white mb-2">Medical History</h2>
              <p className="text-sm sm:text-base text-gray-400">View comprehensive medical history extracted from uploaded documents.</p>
            </div>
            
            {/* Patient Selection for History */}
            <div className="mb-4 sm:mb-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                View History for Patient
              </label>
              <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4">
                <input
                  type="text"
                  placeholder="Enter Patient Number (e.g., P123456)"
                  value={selectedPatientNumber}
                  onChange={(e) => setSelectedPatientNumber(e.target.value.toUpperCase())}
                  className="flex-1 p-3 bg-[#2a2a2a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
                  onKeyPress={(e) => e.key === 'Enter' && verifyPatient()}
                />
                <button
                  onClick={verifyPatient}
                  disabled={searchingPatient || !selectedPatientNumber.trim()}
                  className="bg-blue-600 text-white px-4 sm:px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center text-sm sm:text-base whitespace-nowrap"
                >
                  {searchingPatient ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      Searching...
                    </>
                  ) : (
                    'Find Patient'
                  )}
                </button>
              </div>
              
              {/* Patient Search Result */}
              {patientSearchResult && (
                <div className="mt-3 p-3 bg-green-900/20 border border-green-500/30 rounded-lg">
                  <div className="flex items-center text-green-400">
                    <CheckCircle className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                    <span className="font-medium text-sm sm:text-base">Viewing history for:</span>
                  </div>
                  <div className="mt-1 text-xs sm:text-sm text-gray-300">
                    <p><strong>{patientSearchResult.name}</strong> ({patientSearchResult.patient_number})</p>
                  </div>
                </div>
              )}
            </div>

            {/* Medical History Component */}
            {selectedPatientId && (
              <MedicalHistoryViewer patientId={selectedPatientId} />
            )}

            {!selectedPatientId && (
              <div className="text-center text-gray-500 py-8 sm:py-12">
                <FileText className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-4" />
                <p className="text-base sm:text-lg font-medium">Enter a Patient ID to view medical history</p>
                <p className="text-xs sm:text-sm">Access comprehensive medical records and AI-extracted insights.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Patient Admission Form Popup */}
      {showPatientAdmissionForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-2 sm:p-4 z-50">
          <div className="bg-[#1a1a1a] rounded-lg border border-gray-700 max-w-2xl w-full max-h-[95vh] sm:max-h-[90vh] overflow-y-auto mx-2 sm:mx-0">
            {/* Header */}
            <div className="border-b border-gray-700 px-4 sm:px-6 py-3 sm:py-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg sm:text-xl font-semibold text-white">Patient Admission Form</h2>
                  <p className="text-xs sm:text-sm text-gray-400">Fill in the patient information to complete admission</p>
                </div>
                <button
                  onClick={closePatientAdmissionForm}
                  className="text-gray-400 hover:text-white transition-colors p-1"
                >
                  <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Form Content */}
            <div className="p-4 sm:p-6 space-y-4 sm:space-y-6">
              {/* Required Fields Section */}
              <div>
                <h3 className="text-lg font-medium text-white mb-4">Required Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      First Name <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="text"
                      value={admissionFormData.first_name}
                      onChange={(e) => handleAdmissionFormChange('first_name', e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter first name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Last Name <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="text"
                      value={admissionFormData.last_name}
                      onChange={(e) => handleAdmissionFormChange('last_name', e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter last name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Date of Birth <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="date"
                      value={admissionFormData.date_of_birth}
                      onChange={(e) => handleAdmissionFormChange('date_of_birth', e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Gender</label>
                    <select
                      value={admissionFormData.gender}
                      onChange={(e) => handleAdmissionFormChange('gender', e.target.value)}
                      className="w-full px-3 py-3 sm:py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base sm:text-sm"
                    >
                      <option value="">Select gender</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Contact Information */}
              <div>
                <h3 className="text-lg font-medium text-white mb-4">Contact Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Phone Number</label>
                    <input
                      type="tel"
                      value={admissionFormData.phone}
                      onChange={(e) => handleAdmissionFormChange('phone', e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter phone number"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
                    <input
                      type="email"
                      value={admissionFormData.email}
                      onChange={(e) => handleAdmissionFormChange('email', e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter email address"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-300 mb-2">Home Address</label>
                    <textarea
                      value={admissionFormData.address}
                      onChange={(e) => handleAdmissionFormChange('address', e.target.value)}
                      rows="3"
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter home address"
                    />
                  </div>
                </div>
              </div>

              {/* Emergency Contact */}
              <div>
                <h3 className="text-lg font-medium text-white mb-4">Emergency Contact</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Contact Name</label>
                    <input
                      type="text"
                      value={admissionFormData.emergency_contact_name}
                      onChange={(e) => handleAdmissionFormChange('emergency_contact_name', e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter emergency contact name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Contact Phone</label>
                    <input
                      type="tel"
                      value={admissionFormData.emergency_contact_phone}
                      onChange={(e) => handleAdmissionFormChange('emergency_contact_phone', e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter emergency contact phone"
                    />
                  </div>
                </div>
              </div>

              {/* Medical Information */}
              <div>
                <h3 className="text-lg font-medium text-white mb-4">Medical Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Blood Type</label>
                    <select
                      value={admissionFormData.blood_type}
                      onChange={(e) => handleAdmissionFormChange('blood_type', e.target.value)}
                      className="w-full px-3 py-3 sm:py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base sm:text-sm"
                    >
                      <option value="">Select blood type</option>
                      <option value="A+">A+</option>
                      <option value="A-">A-</option>
                      <option value="B+">B+</option>
                      <option value="B-">B-</option>
                      <option value="AB+">AB+</option>
                      <option value="AB-">AB-</option>
                      <option value="O+">O+</option>
                      <option value="O-">O-</option>
                    </select>
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-300 mb-2">Allergies</label>
                    <textarea
                      value={admissionFormData.allergies}
                      onChange={(e) => handleAdmissionFormChange('allergies', e.target.value)}
                      rows="3"
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="List any known allergies (medications, food, environmental, etc.)"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-300 mb-2">Medical History</label>
                    <textarea
                      value={admissionFormData.medical_history}
                      onChange={(e) => handleAdmissionFormChange('medical_history', e.target.value)}
                      rows="4"
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter relevant medical history, previous conditions, surgeries, etc."
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="border-t border-gray-700 px-4 sm:px-6 py-4 flex flex-col sm:flex-row justify-end space-y-2 sm:space-y-0 sm:space-x-3">
              <button
                onClick={closePatientAdmissionForm}
                disabled={isSubmittingAdmission}
                className="px-4 py-3 sm:py-2 text-gray-400 hover:text-white transition-colors disabled:opacity-50 text-base sm:text-sm"
              >
                Cancel
              </button>
              <button
                onClick={submitPatientAdmission}
                disabled={isSubmittingAdmission}
                className="px-6 py-3 sm:py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-base sm:text-sm"
              >
                {isSubmittingAdmission ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Admitting Patient...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    <span>Admit Patient</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Department Creation Form Popup */}
      {showDepartmentForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-[#2a2a2a] rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="border-b border-gray-700 px-6 py-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white">Department Creation Form</h2>
                <button
                  onClick={closeDepartmentForm}
                  className="text-gray-400 hover:text-white"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            {/* Form Content */}
            <div className="px-6 py-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Basic Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-white border-b border-gray-700 pb-2">
                    Department Information
                  </h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Department Name *
                    </label>
                    <input
                      type="text"
                      value={departmentFormData.name}
                      onChange={(e) => handleDepartmentFormChange('name', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="e.g., Cardiology"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Description
                    </label>
                    <textarea
                      value={departmentFormData.description}
                      onChange={(e) => handleDepartmentFormChange('description', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      rows="3"
                      placeholder="Department description and services"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Head Doctor
                    </label>
                    <select
                      value={departmentFormData.head_doctor_id}
                      onChange={(e) => handleDepartmentFormChange('head_doctor_id', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    >
                      <option value="">Select head doctor (optional)</option>
                      {Array.isArray(userOptions) ? userOptions
                        .filter(user => user.role === 'doctor' || user.role === 'admin')
                        .map(user => (
                          <option key={user.id} value={user.id}>
                            {user.first_name} {user.last_name} ({user.username})
                          </option>
                        )) : []}
                    </select>
                    <p className="text-xs text-gray-400 mt-1">Choose who will head this department</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Floor Number
                    </label>
                    <input
                      type="number"
                      value={departmentFormData.floor_number}
                      onChange={(e) => handleDepartmentFormChange('floor_number', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="e.g., 3"
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-white border-b border-gray-700 pb-2">
                    Contact & Management
                  </h3>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Phone
                    </label>
                    <input
                      type="tel"
                      value={departmentFormData.phone}
                      onChange={(e) => handleDepartmentFormChange('phone', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Department phone number"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Email
                    </label>
                    <input
                      type="email"
                      value={departmentFormData.email}
                      onChange={(e) => handleDepartmentFormChange('email', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="department@hospital.com"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="border-t border-gray-700 px-6 py-4 flex justify-end space-x-3">
              <button
                onClick={closeDepartmentForm}
                disabled={isSubmittingDepartment}
                className="px-4 py-2 text-gray-400 hover:text-white transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={submitDepartment}
                disabled={isSubmittingDepartment}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {isSubmittingDepartment ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Creating Department...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    <span>Create Department</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* User Creation Form Popup */}
      {showUserForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-[#2a2a2a] rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="border-b border-gray-700 px-6 py-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white">User Creation Form</h2>
                <button onClick={closeUserForm} className="text-gray-400 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Username *</label>
                <input
                  type="text"
                  value={userFormData.username}
                  onChange={(e) => handleUserFormChange('username', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="Enter username"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Email *</label>
                <input
                  type="email"
                  value={userFormData.email}
                  onChange={(e) => handleUserFormChange('email', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="Enter email"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">First Name *</label>
                <input
                  type="text"
                  value={userFormData.first_name}
                  onChange={(e) => handleUserFormChange('first_name', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="Enter first name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Last Name *</label>
                <input
                  type="text"
                  value={userFormData.last_name}
                  onChange={(e) => handleUserFormChange('last_name', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="Enter last name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Password Hash *</label>
                <input
                  type="password"
                  value={userFormData.password_hash}
                  onChange={(e) => handleUserFormChange('password_hash', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="Enter password"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Role *</label>
                <select
                  value={userFormData.role}
                  onChange={(e) => handleUserFormChange('role', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="">Select role</option>
                  <option value="admin">Admin</option>
                  <option value="doctor">Doctor</option>
                  <option value="nurse">Nurse</option>
                  <option value="staff">Staff</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Phone</label>
                <input
                  type="tel"
                  value={userFormData.phone}
                  onChange={(e) => handleUserFormChange('phone', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="Enter phone number"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Active Status</label>
                <select
                  value={userFormData.is_active ? "true" : "false"}
                  onChange={(e) => handleUserFormChange('is_active', e.target.value === "true")}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="true">Active</option>
                  <option value="false">Inactive</option>
                </select>
              </div>
            </div>
            <div className="border-t border-gray-700 px-6 py-4 flex justify-end space-x-3">
              <button onClick={closeUserForm} disabled={isSubmittingUser} className="px-4 py-2 text-gray-400 hover:text-white transition-colors disabled:opacity-50">Cancel</button>
              <button onClick={submitUser} disabled={isSubmittingUser} className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2">
                {isSubmittingUser ? (<><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /><span>Creating User...</span></>) : (<><CheckCircle className="w-4 h-4" /><span>Create User</span></>)}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Staff Creation Form Popup */}
      {showStaffForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 sm:p-4">
          <div className="bg-[#2a2a2a] rounded-lg w-full max-w-3xl max-h-[95vh] sm:max-h-[90vh] overflow-y-auto mx-2 sm:mx-0">
            <div className="border-b border-gray-700 px-4 sm:px-6 py-3 sm:py-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg sm:text-xl font-semibold text-white">Staff Creation Form</h2>
                <button onClick={closeStaffForm} className="text-gray-400 hover:text-white p-1">
                  <X className="w-5 h-5 sm:w-6 sm:h-6" />
                </button>
              </div>
            </div>
            <div className="px-4 sm:px-6 py-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Select User *</label>
                    <select
                      value={staffFormData.user_id}
                      onChange={(e) => handleStaffFormChange('user_id', e.target.value)}
                      className="w-full px-3 py-3 sm:py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500 text-base sm:text-sm"
                      disabled={loadingDropdowns}
                    >
                      <option value="">
                        {loadingDropdowns ? 'Loading users...' : 'Select a user'}
                      </option>
                      {Array.isArray(userOptions) ? userOptions.map(user => (
                        <option key={user.id} value={user.id}>
                          {user.first_name} {user.last_name} ({user.username}) - {user.role}
                        </option>
                      )) : []}
                    </select>
                    <p className="text-xs text-gray-400 mt-1">Choose which user this staff record belongs to</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Employee ID *</label>
                    <input
                      type="text"
                      value={staffFormData.employee_id}
                      onChange={(e) => handleStaffFormChange('employee_id', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Employee ID (e.g., EMP001)"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Select Department *</label>
                    <select
                      value={staffFormData.department_id}
                      onChange={(e) => handleStaffFormChange('department_id', e.target.value)}
                      className="w-full px-3 py-3 sm:py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500 text-base sm:text-sm"
                    >
                      <option value="">Select a department</option>
                      {Array.isArray(departmentOptions) ? departmentOptions.map(dept => (
                        <option key={dept.id} value={dept.id}>
                          {dept.name} (Floor {dept.floor_number || 'N/A'})
                        </option>
                      )) : []}
                    </select>
                    <p className="text-xs text-gray-400 mt-1">Choose which department this staff member works in</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Position *</label>
                    <select
                      value={staffFormData.position}
                      onChange={(e) => handleStaffFormChange('position', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    >
                      <option value="">Select position</option>
                      <option value="Doctor">Doctor</option>
                      <option value="Nurse">Nurse</option>
                      <option value="Physician Assistant">Physician Assistant</option>
                      <option value="Medical Technician">Medical Technician</option>
                      <option value="Radiologist">Radiologist</option>
                      <option value="Pharmacist">Pharmacist</option>
                      <option value="Lab Technician">Lab Technician</option>
                      <option value="Receptionist">Receptionist</option>
                      <option value="Administrator">Administrator</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Specialization</label>
                    <input
                      type="text"
                      value={staffFormData.specialization}
                      onChange={(e) => handleStaffFormChange('specialization', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Medical specialization"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">License Number</label>
                    <input
                      type="text"
                      value={staffFormData.license_number}
                      onChange={(e) => handleStaffFormChange('license_number', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Professional license number"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Hire Date *</label>
                    <input
                      type="date"
                      value={staffFormData.hire_date}
                      onChange={(e) => handleStaffFormChange('hire_date', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Salary</label>
                    <input
                      type="number"
                      step="0.01"
                      value={staffFormData.salary}
                      onChange={(e) => handleStaffFormChange('salary', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Annual salary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Shift Pattern</label>
                    <select
                      value={staffFormData.shift_pattern}
                      onChange={(e) => handleStaffFormChange('shift_pattern', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    >
                      <option value="">Select shift pattern</option>
                      <option value="day">Day</option>
                      <option value="night">Night</option>
                      <option value="rotating">Rotating</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Status</label>
                    <select
                      value={staffFormData.status}
                      onChange={(e) => handleStaffFormChange('status', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    >
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                      <option value="on_leave">On Leave</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
            <div className="border-t border-gray-700 px-4 sm:px-6 py-4 flex flex-col sm:flex-row justify-end space-y-2 sm:space-y-0 sm:space-x-3">
              <button 
                onClick={closeStaffForm} 
                disabled={isSubmittingStaff} 
                className="px-4 py-3 sm:py-2 text-gray-400 hover:text-white transition-colors disabled:opacity-50 text-base sm:text-sm"
              >
                Cancel
              </button>
              <button 
                onClick={submitStaff} 
                disabled={isSubmittingStaff} 
                className="px-6 py-3 sm:py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-base sm:text-sm"
              >
                {isSubmittingStaff ? (<><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /><span>Creating Staff...</span></>) : (<><CheckCircle className="w-4 h-4" /><span>Create Staff</span></>)}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Room Creation Form Popup */}
      {showRoomForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-[#2a2a2a] rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="border-b border-gray-700 px-6 py-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white">Room Creation Form</h2>
                <button onClick={closeRoomForm} className="text-gray-400 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Room Number *</label>
                <input
                  type="text"
                  value={roomFormData.room_number}
                  onChange={(e) => handleRoomFormChange('room_number', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="e.g., R101"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Room Type *</label>
                <select
                  value={roomFormData.room_type}
                  onChange={(e) => handleRoomFormChange('room_type', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="">Select room type</option>
                  <option value="patient">Patient Room</option>
                  <option value="icu">ICU</option>
                  <option value="operation">Operation Theater</option>
                  <option value="emergency">Emergency Room</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Capacity</label>
                <input
                  type="number"
                  value={roomFormData.capacity}
                  onChange={(e) => handleRoomFormChange('capacity', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="Number of beds"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Select Department *</label>
                <select
                  value={roomFormData.department_id}
                  onChange={(e) => handleRoomFormChange('department_id', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="">Select a department</option>
                  {Array.isArray(departmentOptions) ? departmentOptions.map(dept => (
                    <option key={dept.id} value={dept.id}>
                      {dept.name} (Floor {dept.floor_number || 'N/A'})
                    </option>
                  )) : []}
                </select>
                <p className="text-xs text-gray-400 mt-1">Choose which department this room belongs to</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Floor Number</label>
                <input
                  type="number"
                  value={roomFormData.floor_number}
                  onChange={(e) => handleRoomFormChange('floor_number', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="Floor number"
                />
              </div>
            </div>
            <div className="border-t border-gray-700 px-6 py-4 flex justify-end space-x-3">
              <button onClick={closeRoomForm} disabled={isSubmittingRoom} className="px-4 py-2 text-gray-400 hover:text-white transition-colors disabled:opacity-50">Cancel</button>
              <button onClick={submitRoom} disabled={isSubmittingRoom} className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2">
                {isSubmittingRoom ? (<><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /><span>Creating Room...</span></>) : (<><CheckCircle className="w-4 h-4" /><span>Create Room</span></>)}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bed Creation Form Popup */}
      {showBedForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-[#2a2a2a] rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="border-b border-gray-700 px-6 py-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white">Bed Creation Form</h2>
                <button onClick={closeBedForm} className="text-gray-400 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Bed Number *</label>
                <input
                  type="text"
                  value={bedFormData.bed_number}
                  onChange={(e) => handleBedFormChange('bed_number', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="e.g., B101"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Select Room *</label>
                <select
                  value={bedFormData.room_id}
                  onChange={(e) => handleBedFormChange('room_id', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  onFocus={() => console.log('🚪 Room dropdown focused. Available rooms:', roomOptions)}
                >
                  <option value="">Select a room ({roomOptions?.length || 0} available)</option>
                  {Array.isArray(roomOptions) ? roomOptions.map(room => (
                    <option key={room.id} value={room.id}>
                      Room {room.room_number} ({room.room_type}) - Floor {room.floor_number || 'N/A'}
                    </option>
                  )) : []}
                </select>
                <p className="text-xs text-gray-400 mt-1">Choose which room this bed will be placed in</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Bed Type</label>
                <select
                  value={bedFormData.bed_type}
                  onChange={(e) => handleBedFormChange('bed_type', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="">Select bed type</option>
                  <option value="standard">Standard</option>
                  <option value="icu">ICU</option>
                  <option value="pediatric">Pediatric</option>
                  <option value="maternity">Maternity</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Status</label>
                <select
                  value={bedFormData.status}
                  onChange={(e) => handleBedFormChange('status', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="">Select status</option>
                  <option value="available">Available</option>
                  <option value="occupied">Occupied</option>
                  <option value="maintenance">Maintenance</option>
                  <option value="reserved">Reserved</option>
                </select>
              </div>
            </div>
            <div className="border-t border-gray-700 px-6 py-4 flex justify-end space-x-3">
              <button onClick={closeBedForm} disabled={isSubmittingBed} className="px-4 py-2 text-gray-400 hover:text-white transition-colors disabled:opacity-50">Cancel</button>
              <button onClick={submitBed} disabled={isSubmittingBed} className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2">
                {isSubmittingBed ? (<><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /><span>Creating Bed...</span></>) : (<><CheckCircle className="w-4 h-4" /><span>Create Bed</span></>)}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Equipment Creation Form Popup */}
      {showEquipmentForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-[#2a2a2a] rounded-lg w-full max-w-3xl max-h-[90vh] overflow-y-auto">
            <div className="border-b border-gray-700 px-6 py-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white">Equipment Creation Form</h2>
                <button onClick={closeEquipmentForm} className="text-gray-400 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            <div className="px-6 py-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Equipment ID * 
                      <span className="text-xs text-gray-400">(e.g., EQ001, EQ002)</span>
                    </label>
                    <input
                      type="text"
                      value={equipmentFormData.equipment_id}
                      onChange={(e) => handleEquipmentFormChange('equipment_id', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="EQ001"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Equipment Name *</label>
                    <input
                      type="text"
                      value={equipmentFormData.name}
                      onChange={(e) => handleEquipmentFormChange('name', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="e.g., X-Ray Machine"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Select Equipment Category *</label>
                    <select
                      value={equipmentFormData.category_id}
                      onChange={(e) => handleEquipmentFormChange('category_id', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    >
                      <option value="">Select a category</option>
                      {Array.isArray(equipmentCategoryOptions) ? equipmentCategoryOptions.map(category => (
                        <option key={category.id} value={category.id}>
                          {category.name}
                        </option>
                      )) : []}
                    </select>
                    <p className="text-xs text-gray-400 mt-1">Choose the equipment category</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Serial Number</label>
                    <input
                      type="text"
                      value={equipmentFormData.serial_number}
                      onChange={(e) => handleEquipmentFormChange('serial_number', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Equipment serial number"
                    />
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Model</label>
                    <input
                      type="text"
                      value={equipmentFormData.model}
                      onChange={(e) => handleEquipmentFormChange('model', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Equipment model"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Purchase Date</label>
                    <input
                      type="date"
                      value={equipmentFormData.purchase_date}
                      onChange={(e) => handleEquipmentFormChange('purchase_date', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Location</label>
                    <input
                      type="text"
                      value={equipmentFormData.location}
                      onChange={(e) => handleEquipmentFormChange('location', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Equipment location"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Manufacturer</label>
                    <input
                      type="text"
                      value={equipmentFormData.manufacturer}
                      onChange={(e) => handleEquipmentFormChange('manufacturer', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Manufacturer name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Warranty Expiry</label>
                    <input
                      type="date"
                      value={equipmentFormData.warranty_expiry}
                      onChange={(e) => handleEquipmentFormChange('warranty_expiry', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Status</label>
                    <select
                      value={equipmentFormData.status}
                      onChange={(e) => handleEquipmentFormChange('status', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    >
                      <option value="">Select status</option>
                      <option value="operational">Operational</option>
                      <option value="maintenance">Maintenance</option>
                      <option value="out_of_order">Out of Order</option>
                      <option value="retired">Retired</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Price</label>
                    <input
                      type="number"
                      step="0.01"
                      value={equipmentFormData.price}
                      onChange={(e) => handleEquipmentFormChange('price', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Purchase price"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Select Department</label>
                    <select
                      value={equipmentFormData.department_id}
                      onChange={(e) => handleEquipmentFormChange('department_id', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    >
                      <option value="">Select a department (optional)</option>
                      {Array.isArray(departmentOptions) ? departmentOptions.map(dept => (
                        <option key={dept.id} value={dept.id}>
                          {dept.name} (Floor {dept.floor_number || 'N/A'})
                        </option>
                      )) : []}
                    </select>
                    <p className="text-xs text-gray-400 mt-1">Choose which department will use this equipment</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Last Maintenance</label>
                    <input
                      type="date"
                      value={equipmentFormData.last_maintenance}
                      onChange={(e) => handleEquipmentFormChange('last_maintenance', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Next Maintenance</label>
                    <input
                      type="date"
                      value={equipmentFormData.next_maintenance}
                      onChange={(e) => handleEquipmentFormChange('next_maintenance', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Notes</label>
                    <textarea
                      value={equipmentFormData.notes}
                      onChange={(e) => handleEquipmentFormChange('notes', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      rows="3"
                      placeholder="Additional notes"
                    />
                  </div>
                </div>
              </div>
            </div>
            <div className="border-t border-gray-700 px-6 py-4 flex justify-end space-x-3">
              <button onClick={closeEquipmentForm} disabled={isSubmittingEquipment} className="px-4 py-2 text-gray-400 hover:text-white transition-colors disabled:opacity-50">Cancel</button>
              <button onClick={submitEquipment} disabled={isSubmittingEquipment} className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2">
                {isSubmittingEquipment ? (<><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /><span>Creating Equipment...</span></>) : (<><CheckCircle className="w-4 h-4" /><span>Create Equipment</span></>)}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Supply Creation Form Popup */}
      {showSupplyForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-[#2a2a2a] rounded-lg w-full max-w-3xl max-h-[90vh] overflow-y-auto">
            <div className="border-b border-gray-700 px-6 py-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white">Supply Creation Form</h2>
                <button onClick={closeSupplyForm} className="text-gray-400 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            <div className="px-6 py-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Item Code * 
                      <span className="text-xs text-gray-400">(e.g., SUP001, MED001)</span>
                    </label>
                    <input
                      type="text"
                      value={supplyFormData.item_code}
                      onChange={(e) => handleSupplyFormChange('item_code', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="SUP001"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Supply Name *</label>
                    <input
                      type="text"
                      value={supplyFormData.name}
                      onChange={(e) => handleSupplyFormChange('name', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="e.g., Surgical Gloves"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Select Supply Category *</label>
                    <select
                      value={supplyFormData.category_id}
                      onChange={(e) => handleSupplyFormChange('category_id', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    >
                      <option value="">Select a category</option>
                      {Array.isArray(supplyCategoryOptions) ? supplyCategoryOptions.map(category => (
                        <option key={category.id} value={category.id}>
                          {category.name}
                        </option>
                      )) : []}
                    </select>
                    <p className="text-xs text-gray-400 mt-1">Choose the supply category</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Current Stock</label>
                    <input
                      type="number"
                      value={supplyFormData.current_stock}
                      onChange={(e) => handleSupplyFormChange('current_stock', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Current stock quantity"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Minimum Stock Level</label>
                    <input
                      type="number"
                      value={supplyFormData.minimum_stock_level}
                      onChange={(e) => handleSupplyFormChange('minimum_stock_level', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Minimum stock level"
                    />
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Unit of Measure *</label>
                    <input
                      type="text"
                      value={supplyFormData.unit_of_measure}
                      onChange={(e) => handleSupplyFormChange('unit_of_measure', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="e.g., pieces, boxes, liters"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Supplier</label>
                    <input
                      type="text"
                      value={supplyFormData.supplier}
                      onChange={(e) => handleSupplyFormChange('supplier', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Supplier name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Unit Cost</label>
                    <input
                      type="number"
                      step="0.01"
                      value={supplyFormData.unit_cost}
                      onChange={(e) => handleSupplyFormChange('unit_cost', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Cost per unit"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Expiry Date</label>
                    <input
                      type="date"
                      value={supplyFormData.expiry_date}
                      onChange={(e) => handleSupplyFormChange('expiry_date', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Maximum Stock Level</label>
                    <input
                      type="number"
                      value={supplyFormData.maximum_stock_level}
                      onChange={(e) => handleSupplyFormChange('maximum_stock_level', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Maximum stock level"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Location</label>
                    <input
                      type="text"
                      value={supplyFormData.location}
                      onChange={(e) => handleSupplyFormChange('location', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Storage location"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
                    <textarea
                      value={supplyFormData.description}
                      onChange={(e) => handleSupplyFormChange('description', e.target.value)}
                      className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                      placeholder="Supply description"
                      rows="3"
                    />
                  </div>
                </div>
              </div>
            </div>
            <div className="border-t border-gray-700 px-6 py-4 flex justify-end space-x-3">
              <button onClick={closeSupplyForm} disabled={isSubmittingSupply} className="px-4 py-2 text-gray-400 hover:text-white transition-colors disabled:opacity-50">Cancel</button>
              <button onClick={submitSupply} disabled={isSubmittingSupply} className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2">
                {isSubmittingSupply ? (<><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /><span>Creating Supply...</span></>) : (<><CheckCircle className="w-4 h-4" /><span>Create Supply</span></>)}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Legacy User Creation Form Popup */}
      {showLegacyUserForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-[#2a2a2a] rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="border-b border-gray-700 px-6 py-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white">Legacy User Creation Form</h2>
                <button onClick={closeLegacyUserForm} className="text-gray-400 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Name *</label>
                <input
                  type="text"
                  value={legacyUserFormData.name}
                  onChange={(e) => handleLegacyUserFormChange('name', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="Enter full name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Email *</label>
                <input
                  type="email"
                  value={legacyUserFormData.email}
                  onChange={(e) => handleLegacyUserFormChange('email', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="Enter email address"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Address *</label>
                <textarea
                  value={legacyUserFormData.address}
                  onChange={(e) => handleLegacyUserFormChange('address', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="Enter full address"
                  rows="3"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Phone *</label>
                <input
                  type="tel"
                  value={legacyUserFormData.phone}
                  onChange={(e) => handleLegacyUserFormChange('phone', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="Enter phone number"
                />
              </div>
            </div>
            <div className="border-t border-gray-700 px-6 py-4 flex justify-end space-x-3">
              <button onClick={closeLegacyUserForm} disabled={isSubmittingLegacyUser} className="px-4 py-2 text-gray-400 hover:text-white transition-colors disabled:opacity-50">Cancel</button>
              <button onClick={submitLegacyUser} disabled={isSubmittingLegacyUser} className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2">
                {isSubmittingLegacyUser ? (<><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /><span>Creating Legacy User...</span></>) : (<><CheckCircle className="w-4 h-4" /><span>Create Legacy User</span></>)}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Equipment Category Creation Form Popup */}
      {showEquipmentCategoryForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-[#2a2a2a] rounded-lg w-full max-w-xl max-h-[90vh] overflow-y-auto">
            <div className="border-b border-gray-700 px-6 py-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white">Equipment Category Creation</h2>
                <button onClick={closeEquipmentCategoryForm} className="text-gray-400 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Category Name *</label>
                <input
                  type="text"
                  value={equipmentCategoryFormData.name}
                  onChange={(e) => handleEquipmentCategoryFormChange('name', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="e.g., Diagnostic Equipment, Surgical Instruments"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Description (Optional)</label>
                <textarea
                  value={equipmentCategoryFormData.description}
                  onChange={(e) => handleEquipmentCategoryFormChange('description', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="Brief description of this category"
                  rows="3"
                />
              </div>
            </div>
            <div className="border-t border-gray-700 px-6 py-4 flex justify-end space-x-3">
              <button onClick={closeEquipmentCategoryForm} disabled={isSubmittingEquipmentCategory} className="px-4 py-2 text-gray-400 hover:text-white transition-colors disabled:opacity-50">Cancel</button>
              <button onClick={submitEquipmentCategory} disabled={isSubmittingEquipmentCategory} className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2">
                {isSubmittingEquipmentCategory ? (<><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /><span>Creating Category...</span></>) : (<><CheckCircle className="w-4 h-4" /><span>Create Category</span></>)}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Supply Category Creation Form Popup */}
      {showSupplyCategoryForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-[#2a2a2a] rounded-lg w-full max-w-xl max-h-[90vh] overflow-y-auto">
            <div className="border-b border-gray-700 px-6 py-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white">Supply Category Creation</h2>
                <button onClick={closeSupplyCategoryForm} className="text-gray-400 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Category Name *</label>
                <input
                  type="text"
                  value={supplyCategoryFormData.name}
                  onChange={(e) => handleSupplyCategoryFormChange('name', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="e.g., Medications, Surgical Supplies"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Description (Optional)</label>
                <textarea
                  value={supplyCategoryFormData.description}
                  onChange={(e) => handleSupplyCategoryFormChange('description', e.target.value)}
                  className="w-full px-3 py-2 bg-[#1a1a1a] border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  placeholder="Brief description of this category"
                  rows="3"
                />
              </div>
            </div>
            <div className="border-t border-gray-700 px-6 py-4 flex justify-end space-x-3">
              <button onClick={closeSupplyCategoryForm} disabled={isSubmittingSupplyCategory} className="px-4 py-2 text-gray-400 hover:text-white transition-colors disabled:opacity-50">Cancel</button>
              <button onClick={submitSupplyCategory} disabled={isSubmittingSupplyCategory} className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2">
                {isSubmittingSupplyCategory ? (<><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /><span>Creating Category...</span></>) : (<><CheckCircle className="w-4 h-4" /><span>Create Category</span></>)}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DirectMCPChatbot;
