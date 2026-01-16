import React from 'react';
import Navbar from './components/Navbar/Navbar.jsx';
import Footer from './components/Footer/Footer.jsx';
import Form from './components/Form/Form.jsx';
export default function Evaluate() {
    return (
        <div className="min-h-screen flex flex-col justify-between">
            <Navbar /> 
            <Form />
            <Footer />
            </div>
    );
}