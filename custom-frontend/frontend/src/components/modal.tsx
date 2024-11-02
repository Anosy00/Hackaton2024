import React, { useState } from 'react';
import { setUser } from './leftbar'

type propTypes = {
    title: string;
    open: boolean;
    onClose: () => void;
    children: React.ReactNode;
}

export const Modal: React.FC<propTypes> = ({ open, onClose, children, title }) => {
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const loginCreate = async (email: string, username: string, password: string): Promise<void> => {
        try {
            if (title === "Login") {
                console.log("Login");
                // Add your login logic here if needed
            } else {
                const response = await fetch(`http://127.0.0.1/users/?email=${email}&username=${username}&password=${password}`, {
                    method: 'POST',
                    mode: 'no-cors', // no-cors, *cors, same-origin
                    headers: {
                        'Content-Type': 'application/json' // Set appropriate content type
                    },
                    body: JSON.stringify({ email, username, password }) // If you're sending a JSON body
                });
    
                const data = await response.json(); // Assuming the server responds with JSON
                console.log(data); // Do something with the response data
            }
        } catch (error) {
            console.error("Error during fetch:", error); // Handle errors
        }
    };
    

    return (
        <div className={`fixed inset-0 flex justify-center items-center transition-colors ${open ? "visible bg-black/20" : "invisible"}`}>
            <div className='w-1/4 bg-white rounded-3xl flex flex-col justify-center items-center p-4'>
                <h1 className='font-bold mb-4'>{title}</h1>
                <input
                    type="text"
                    placeholder="Email"
                    className='border-2 border-black rounded-lg p-2 w-full'
                    value={email}
                    onChange={(e) => setEmail(e.target.value)} // Met à jour l'état
                />
                <input
                    type="text"
                    placeholder="Username"
                    className='border-2 border-black rounded-lg p-2 w-full'
                    value={username}
                    onChange={(e) => setUsername(e.target.value)} // Met à jour l'état
                />
                <input
                    type="password"
                    placeholder="Password"
                    className='border-2 border-black rounded-lg p-2 w-full mt-5'
                    value={password}
                    onChange={(e) => setPassword(e.target.value)} // Met à jour l'état
                />

                <div className='flex flex-row justify-around space-x-4 mt-4 w-full'>
                    <button className='bg-blue-500 text-white rounded-lg p-2 flex-1' onClick={onClose}>Cancel</button>
                    <button className='bg-blue-500 text-white rounded-lg p-2 flex-1' onClick={() => {
                        console.log(email + " EMAILLLL");
                        loginCreate(email, username, password);
                        setUser(username);
                        onClose();
                    }}>{title}</button>
                </div>
            </div>
        </div>
    );


}