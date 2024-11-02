import { Button } from "./ui/button";

export function LeftBar() {
    return (
        <div className="leftbar w-1/5" style={{backgroundColor:'#242624'}}>
            <div className="leftbar__header flex flex-row justify-around">
                <h2 className="text-xl font-bold text-white">Ex pas triés ChatBot</h2>
                <Button className="bg-green-500 text-white">Login</Button>
            </div>
            <div className="leftbar__content w-full">
                <h3 className="text-white text-lg font-bold">Anciennes conversations</h3>
                <ul>
                    <li className="text-white flex justify-start"><Button className="bg-transparent w-full">Conversation</Button></li>
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