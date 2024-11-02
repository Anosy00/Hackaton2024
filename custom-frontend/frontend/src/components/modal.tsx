import React from 'react';

type propTypes = {
    title: string;
    open: boolean;
    onClose: () => void;
    children: React.ReactNode;
}

export const Modal: React.FC<propTypes> = ({open, onClose, children, title}) => {
    return (
        <div className={`fixed inset-0 flex justify-center items-center transition-colors ${open ? "visible bg-black/20" : "invisible"}`}>
            <div className='w-1/4 bg-white rounded-3xl flex flex-col justify-center items-center p-4'>
                <h1 className='font-bold mb-4'>{title}</h1>
                <input type="text" placeholder="Username" className='border-2 border-black rounded-lg p-2 w-full'/>
                <input type="password" placeholder="Password" className='border-2 border-black rounded-lg p-2 w-full mt-5'/>
                
                {/* Conteneur pour les boutons */}
                <div className='flex flex-row justify-around space-x-4 mt-4 w-full'>
                    <button className='bg-blue-500 text-white rounded-lg p-2 flex-1' onClick={onClose}>Cancel</button>
                    <button className='bg-blue-500 text-white rounded-lg p-2 flex-1' onClick={onClose}>Login</button>
                </div>
            </div>
        </div>
    );
    
    
}