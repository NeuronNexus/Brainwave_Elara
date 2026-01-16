import React from 'react';
import Navbar from './components/Navbar/Navbar.jsx';
import Footer from './components/Footer/Footer.jsx';
export default function Landing() {
    return (
        <div className="min-h-screen flex flex-col justify-between">
            <Navbar />
            
            {/* GIF Container with vertical spacing (py-10) to prevent touching nav/footer */}
            <main className="w-full py-10">
                <img 
                    src="https://i.pinimg.com/originals/90/70/32/9070324cdfc07c68d60eed0c39e77573.gif"
                    className="w-full h-auto object-cover" 
                />
            </main>

            <Footer />
        </div>
    );
}