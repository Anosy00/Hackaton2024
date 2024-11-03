import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useState, useEffect, useRef } from "react";
import { useChatInteract, useChatMessages, IStep } from "@chainlit/react-client";

interface Response {
  content: string;
}

type MessageType = "user_message" | "assistant_message";

interface Message {
  name: string;
  type: MessageType;
  output: string;
}

async function uploadFiles() {
    const form = document.getElementById("uploadForm") as HTMLFormElement;
    const formData = new FormData(form);
    

    const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
    });

    const result = await response.json();
    document.getElementById("response")!.innerText = JSON.stringify(result, null, 2);
}

export default function UploadComponent() {
    return (
        <div>
            <form id="uploadForm" encType="multipart/form-data">
                <input type="file" name="file" multiple />
                <button type="button" onClick={uploadFiles}>Téléverser</button>
            </form>
            <div id="response"></div>
        </div>
    );
}


export function Playground() {
  const [inputValue, setInputValue] = useState<string>("");
  const { sendMessage } = useChatInteract();
  const { messages } = useChatMessages();
  const [reactions, setReactions] = useState<{ [key: string]: string | null }>({});
  
  // Variable pour stocker le nom du fichier sélectionné
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);

  // Variable de défilement
  const messagesEndRef = useRef<HTMLDivElement>(null); 

  // Variable d'état pour le thème
  const [isDarkTheme, setIsDarkTheme] = useState<boolean>(true);

  const sendApiMessage = async () => {
    if (inputValue.trim() === "") return;

    try {
      const response = await fetch("http://localhost:8000", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ content: inputValue }),
      });

      const data: Response = await response.json();
      const botMessage: Message = {
        name: "Bot",
        type: "assistant_message",
        output: data.content,
      };
      sendMessage(botMessage, []);
      setInputValue("");
    } catch (error) {
      console.error("Erreur lors de l'envoi du message:", error);
    }
  };

  const handleSendMessage = (user: string) => {
    const content = inputValue.trim();
    if (content) {
      const userMessage: Message = {
        name: user,
        type: "user_message",
        output: content,
      };
      if (content === "rick roll"){
        window.location.href = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";
      }
      sendMessage(userMessage, []);
      setInputValue("");
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setSelectedFileName(file.name); // Met à jour le nom du fichier sélectionné

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        console.log("Fichier téléchargé et indexé avec succès");
      } else {
        console.error("Erreur lors du téléchargement du fichier:", await response.json());
      }
    } catch (error) {
      console.error("Erreur lors du téléchargement du fichier:", error);
    }
  };

  const renderMessage = (message: IStep) => {
    const dateOptions: Intl.DateTimeFormatOptions = {
      hour: "2-digit",
      minute: "2-digit",
    };
    const date = new Date(message.createdAt).toLocaleTimeString(undefined, dateOptions);
    const currentReaction = reactions[message.id];

    const handleReact = (messageId: string, reaction: string) => {
      setReactions((prevReactions) => ({
        ...prevReactions,
        [messageId]: prevReactions[messageId] === reaction ? null : reaction,
      }));
    };

    return (
        <div key={message.id} className={`flex ${message.type === "user_message" ? "justify-end" : "justify-start"} mb-4`}>
          <div className={`max-w-xl p-3 rounded-lg
        ${message.type === "user_message" ? "bg-blue-500 text-white" : (isDarkTheme ? "bg-gray-800 text-white" : "bg-gray-200 text-black")}
        relative`}>
            <p>{message.output}</p>
            <small className="absolute bottom-1 right-1 text-xs text-gray-500">{date}</small>
            {message.type === "assistant_message" && (
                <div className="mt-2 flex space-x-2">
                      <button
                          onClick={() => {handleReact(message.id, "like");}}
                          className={`w-8 h-8 flex items-center justify-center rounded ${currentReaction === "like" ? "bg-green-500 text-white" : (isDarkTheme ? 'bg-gray-900' : 'bg-gray-300 text-black')} text-xs`}
                      >
                        👍
                      </button>
                      <button
                          onClick={() => {handleReact(message.id, "unlike");}}
                          className={`w-8 h-8 flex items-center justify-center rounded ${currentReaction === "unlike" ? "bg-red-500 text-white" : (isDarkTheme ? 'bg-gray-900' : 'bg-gray-300 text-black')} text-xs`}
                      >
                        👎
                      </button>
                </div>
            )}
          </div>
        </div>
    );
  };

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  return (
      <div className={`min-h-screen ${isDarkTheme ? 'bg-gray-900' : 'bg-white'} flex flex-col transition-colors duration-300 w-4/5`}>
        <div className="flex-1 overflow-auto p-6">
          <div className="h-[800px] overflow-hidden p-6" >
            <div className="space-y-4">
              {messages.map((msg) => renderMessage(msg))}
              <div ref={messagesEndRef} />
            </div>
          </div>
        </div>
        <div className={`border-0 p-4 ${isDarkTheme ? 'bg-gray-800' : 'bg-gray-200'}`}>
          <form id="uploadForm" encType="multipart/form-data">
            <input type="file" name="file" multiple/>
            <button type="button" onClick={uploadFiles}>Téléverser</button>
          </form>
          <div id="response"></div>
          <div className="flex items-center space-x-2">
            <Input
                autoFocus
                className={`flex-1 ${isDarkTheme ? 'bg-gray-900 text-white border-0' : 'bg-white text-black'}`}
                id="message-input"
                placeholder="Type a message"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyUp={(e) => {
                  if (e.key === "Enter") {
                    handleSendMessage("User");
                  }
                }}
            />
            <Button onClick={sendApiMessage}>Send</Button>
            <Button onClick={() => setIsDarkTheme(!isDarkTheme)}>
              {isDarkTheme ? 'Light Mode' : 'Dark Mode'}
            </Button>

            {/* Input pour le fichier */}
            <input
              type="file"
              accept=".pdf,.txt,.docx"
              onChange={handleFileUpload}
              className="hidden" // Masque le champ de fichier
              id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <input type="file" accept=".pdf,.txt,.docx" onChange={handleFileUpload}/>
            </label>
          </div>
        </div>
      </div>
  );
}
