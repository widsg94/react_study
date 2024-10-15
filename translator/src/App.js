import React, { useState, useRef } from 'react';
import axios from 'axios';

const App = () => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [isCapturing, setIsCapturing] = useState(false);
    const [identifiedText, setIdentifiedText] = useState('');
    const [hiraganaText, setHiraganaText] = useState('');
    const [translatedText, setTranslatedText] = useState('');
    const captureIntervalRef = useRef(null);

    const startCapture = async () => {
        try {
            if (captureIntervalRef.current) {
                console.log("Capture is already running");
                return;  // Prevent setting a new interval if one is already running
            }

            const stream = await navigator.mediaDevices.getDisplayMedia({
                video: true,
                audio: false,
            });
            videoRef.current.srcObject = stream;
            videoRef.current.play();
            setIsCapturing(true);

            // Start text extraction every 2 seconds
            captureIntervalRef.current = setInterval(() => {
                captureFrame();
            }, 2000);

        } catch (error) {
            console.error("Error capturing screen:", error);
        }
    };

    const stopCapture = () => {
        const stream = videoRef.current.srcObject;
        const tracks = stream.getTracks();

        tracks.forEach((track) => track.stop());
        videoRef.current.srcObject = null;
        setIsCapturing(false);
        setIdentifiedText('');
        setHiraganaText('');
        setTranslatedText('');

        if (captureIntervalRef.current) {
            clearInterval(captureIntervalRef.current);
            captureIntervalRef.current = null;
        }
    };

    const captureFrame = async () => {
        console.log('Capturing frame');

        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');

        const videoWidth = videoRef.current.videoWidth;
        const videoHeight = videoRef.current.videoHeight;

        canvas.width = videoWidth;
        canvas.height = videoHeight;

        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

        const imageDataURL = canvas.toDataURL('image/png');

        // Use OCR service to recognize Japanese text
        try {
            const response = await axios.post('http://127.0.0.1:5000/api/ocr', {
                image_data: imageDataURL,
            });

            if (response.status === 429) {
                console.log("OCR is currently in progress. Please wait.");
                return; // Do not proceed with translation if OCR is locked
            }

            // Only update if there is new recognized text
            if (response.data.text) {
                setIdentifiedText(response.data.text);  // Update identified text
            }

            const translationResponse = await axios.post('http://127.0.0.1:5002/api/kanji_to_hiragana', {
                text: response.data.text || identifiedText,
            });

            if (translationResponse.data && translationResponse.data.hiragana_text) {
                setHiraganaText(translationResponse.data.hiragana_text);  // Update Hiragana text
            }

            // Korean translation (no change needed here)
            const koreanTranslationResponse = await axios.post('http://127.0.0.1:5001/api/korean', {
                sentence: response.data.text || identifiedText,
            });
            setTranslatedText(koreanTranslationResponse.data.translated_text); // Update translated text
        } catch (error) {
            console.error("Error during OCR processing or translation:", error);
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
            <h1 style={{ textAlign: 'center' }}>Real-time Translator v4.2</h1>
            <div
                style={{
                    flex: 2,
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'flex-start',
                    width: '100%',
                    height: '50vh',
                    overflow: 'hidden',
                    paddingBottom: '10px',
                }}
            >
                <div
                    style={{
                        border: '1px solid black',
                        width: '70vw',
                        maxWidth: '900px',
                        height: '100%',
                    }}
                >
                    <video
                        ref={videoRef}
                        style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'contain',
                        }}
                        autoPlay
                        muted
                    />
                    <canvas ref={canvasRef} style={{ display: 'block', width: '100%', height: '100%' }} />
                </div>
            </div>

            {/* Updated Layout for Identified and Hiragana Text */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '20px' }}>
                <div style={{ display: 'flex', flexDirection: 'row', marginBottom: '10px' }}>
                    <div style={{ flex: 1, marginRight: '10px' }}>
                        <h2>Identified Text:</h2>
                        <div
                            style={{
                                border: '1px solid #ccc',
                                padding: '10px',
                                minHeight: '100px',
                                overflowY: 'auto',
                            }}
                        >
                            {identifiedText ? (
                                <div dangerouslySetInnerHTML={{ __html: identifiedText }} />
                            ) : (
                                'No text identified yet.'
                            )}
                        </div>
                    </div>

                    <div style={{ flex: 1 }}>
                        <h2>Hiragana Text:</h2>
                        <div
                            style={{
                                border: '1px solid #ccc',
                                padding: '10px',
                                minHeight: '100px',
                                overflowY: 'auto',
                            }}
                        >
                            {hiraganaText ? (
                                <div dangerouslySetInnerHTML={{ __html: hiraganaText }} />
                            ) : (
                                'No Hiragana available yet.'
                            )}
                        </div>
                    </div>
                </div>

                {/* Korean Text Below */}
                <div style={{ marginBottom: '10px' }}>
                    <h2>Korean Translated Text:</h2>
                    <div
                        style={{
                            border: '1px solid #ccc',
                            padding: '10px',
                            minHeight: '100px',
                            overflowY: 'auto',
                        }}
                    >
                        {translatedText ? (
                            <div dangerouslySetInnerHTML={{ __html: translatedText }} />
                        ) : (
                            'No translation available yet.'
                        )}
                    </div>
                </div>
            </div>

            <div style={{ padding: '20px' }}>
                <h2>{isCapturing ? 'Capturing...' : 'Select a Page to Monitor'}</h2>
                <div style={{ margin: '20px 0' }}>
                    {!isCapturing ? (
                        <button onClick={startCapture} style={{ padding: '10px 20px' }}>
                            Start Capture
                        </button>
                    ) : (
                        <button onClick={stopCapture} style={{ padding: '10px 20px' }}>
                            Stop Capture
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default App;
