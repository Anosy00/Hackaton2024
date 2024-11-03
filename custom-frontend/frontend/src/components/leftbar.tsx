import { useState } from "react";
import { Button } from "./ui/button";
import { Modal } from "./modal";
import { __USER__ } from "../global.d";
import { useChatInteract } from "@chainlit/react-client";


var user: string;

export function LeftBar() {
    const [openLogin, setOpenLogin] = useState<boolean>(false);
    const [openCreate, setOpenCreate] = useState<boolean>(false);

    const { clear } = useChatInteract();
    
    return (
        <div className="leftbar w-1/5" style={{backgroundColor:'#242624'}}>
            <div className="leftbar__header flex flex-col justify-center">
                <p className="text-white">Utilisateur connecté : {user}</p>
                <h2 className="text-xl font-bold text-white">Ex pas triés ChatBot</h2>
                <div className="flex flex-row flex-around">
                    <Button className="bg-green-500 text-white" onClick={() => setOpenLogin(true)}>Login</Button>
                    <Button className="bg-green-500 text-white" onClick={() => setOpenCreate(true)}>Create Account</Button>
                </div>
                <Button className="bg-green-500 text-white" onClick={() => clear()}>New Conversation</Button>
                
            </div>
            <Modal title="Login" open={openLogin} onClose={() => setOpenLogin(false)} children={undefined}></Modal>
            <Modal title="Create" open={openCreate} onClose={() => setOpenCreate(false)} children={undefined}></Modal>
            <div className="leftbar__content w-full">
                <h3 className="text-white text-lg font-bold">Anciennes conversations</h3>
                <ul>
                    <li className="text-white flex justify-start"><Button className="bg-transparent w-full"></Button></li>
                    <li className="text-white flex justify-start"><Button className="bg-transparent w-full">Conversation</Button></li>
                    <li className="text-white flex justify-start"><Button className="bg-transparent w-full">Conversation</Button></li>
                    <li className="text-white flex justify-start"><Button className="bg-transparent w-full">Conversation</Button></li>
                    <li className="text-white flex justify-start"><Button className="bg-transparent w-full">Conversation</Button></li>
                    <li className="text-white flex justify-start"><Button className="bg-transparent w-full">Conversation</Button></li>
                    <li className="text-white flex justify-start"><Button className="bg-transparent w-full">Conversation</Button></li>
                </ul>
            </div>
        </div>
    );
}

export function setUser(username: string) {
    user = username;
}