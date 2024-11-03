import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useState } from "react";
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

export function Playground() {
  const [inputValue, setInputValue] = useState<string>("");
  const { sendMessage } = useChatInteract();
  const { messages } = useChatMessages();
  const [reactions, setReactions] = useState<{ [key: string]: string | null }>({});
  const [currentConversationId, setCurrentConversationId] = useState<number>();
  

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

  const handleSendMessage = async (user: string) => {
    const content = inputValue.trim();
    if (content) {
      const userMessage: Message = {
        name: user,
        type: "user_message",
        output: content,
      };
      sendMessage(userMessage, []);
      setInputValue("");
    }
    try {
      const response = await fetch("http:127.0.0.1/", {
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
        ${message.type === "user_message" ?
              ("bg-blue-500 text-white") :
              (isDarkTheme ? "bg-gray-800 text-white" : "bg-gray-200 text-black")}
        relative`}>
            <p>{message.output}</p>
            <small className="absolute bottom-1 right-1 text-xs text-gray-500">{date}</small>
            {message.type === "assistant_message" && ( //&& (isLastMessage || reactions[message.id] === "like" || reactions[message.id] === "unlike")
                <div className="mt-2 flex space-x-2">
                      <button
                          onClick={() => {handleReact(message.id, "like");}}
                          className={`w-8 h-8 flex items-center justify-center rounded ${currentReaction === "like" ? "bg-green-500 text-white" : "bg-gray-300 text-black"} text-xs`}
                      >
                        👍
                      </button>
                      <button
                          onClick={() => {handleReact(message.id, "unlike");}}
                          className={`w-8 h-8 flex items-center justify-center rounded ${currentReaction === "unlike" ? "bg-red-500 text-white" : "bg-gray-300 text-black"} text-xs`}
                      >
                        👎
                      </button>
                </div>
            )}
          </div>
        </div>
    );
  };

  return (
      <div className={`min-h-screen ${isDarkTheme ? 'bg-gray-900' : 'bg-white'} flex flex-col transition-colors duration-300 w-4/5`}>
        <div className="flex-1 overflow-auto p-6">
          <div className="space-y-4">
            {messages.map((msg) => renderMessage(msg))}
          </div>
        </div>
        <div className={`border-0 p-4 ${isDarkTheme ? 'bg-gray-800' : 'bg-gray-200'}`}>
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
          </div>
        </div>
      </div>
  );
}
