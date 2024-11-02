import React from 'react';
import { setUser } from './leftbar'

type propTypes = {
    title: string;
    open: boolean;
    onClose: () => void;
    children: React.ReactNode;
}

export const Modal: React.FC<propTypes> = ({ open, onClose, children, title }) => {

    const loginCreate = async (email: string, username: string, password: string): Promise<void> => {
        try {
            if (title === "Login") {
                console.log("Login");
                // Add your login logic here if needed
            } else {
                const response = await fetch(`http://127.0.0.1/users/?email=${encodeURIComponent(email)}&username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`, {
                    method: 'POST',
                    mode: 'no-cors', // no-cors, *cors, same-origin
                    headers: {
                        'Content-Type': 'application/json' // Set appropriate content type
                    },
                    body: JSON.stringify({ email, username, password }) // If you're sending a JSON body
                });
    
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`); // Handle errors appropriately
                }
    
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
                <input type="text" placeholder="Email" className='border-2 border-black rounded-lg p-2 w-full' id='userEmail'/>
                <input type="text" placeholder="Username" className='border-2 border-black rounded-lg p-2 w-full' id='userUsername'/>
                <input type="password" placeholder="Password" className='border-2 border-black rounded-lg p-2 w-full mt-5' id='userPassword'/>

                {/* Conteneur pour les boutons */}
                <div className='flex flex-row justify-around space-x-4 mt-4 w-full'>
                    <button className='bg-blue-500 text-white rounded-lg p-2 flex-1' onClick={onClose}>Cancel</button>
                    <button className='bg-blue-500 text-white rounded-lg p-2 flex-1' onClick={() => {
                        loginCreate((document.getElementById('userEmail') as HTMLInputElement).value,
                        (document.getElementById('userUsername') as HTMLInputElement).value,
                        (document.getElementById('userPassword') as HTMLInputElement).value);
                        setUser((document.getElementById('userUsername') as HTMLInputElement).value);
                        onClose();
                    }}>{title}</button>
                </div>
            </div>
        </div>
    );


}