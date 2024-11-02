import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { useChatInteract, useChatMessages, IStep } from "@chainlit/react-client";

interface Response {
  content: string; // Changez ceci pour correspondre à la structure de réponse de votre API
}

type MessageType = "user_message" | "assistant_message"; // Définition des types littéraux

interface Message {
  name: string;
  type: MessageType; // Utilisation du type MessageType
  output: string;
}

export function Playground() {
  const [inputValue, setInputValue] = useState<string>("");
  const { sendMessage } = useChatInteract();
  const { messages } = useChatMessages();
  const [reactions, setReactions] = useState<{ [key: string]: string | null }>({});

  const sendApiMessage = async () => {
    if (inputValue.trim() === "") return;

    try {
      const response = await fetch("http://localhost:8000", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ content: inputValue }), // Utilise inputValue pour l'API
      });

      const data: Response = await response.json();
      // Envoyer le message à Chainlit après avoir reçu la réponse
      const botMessage: Message = {
        name: "Bot",
        type: "assistant_message", // Utilisation correcte du type littéral
        output: data.content,
      };
      sendMessage(botMessage, []);
      setInputValue(""); // Réinitialise le champ de message
    } catch (error) {
      console.error("Erreur lors de l'envoi du message:", error);
    }
  };

  const handleSendMessage = (user: string) => {
    const content = inputValue.trim();
    if (content) {
      const userMessage: Message = {
        name: user,
        type: "user_message", // Utilisation correcte du type littéral
        output: content, // Envoie l'inputValue comme message utilisateur
      };
      sendMessage(userMessage, []); // Envoie le message utilisateur à Chainlit
      setInputValue(""); // Réinitialise l'input après l'envoi
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
      // Enregistre la nouvelle réaction, ou remet à null si déjà sélectionnée
      setReactions((prevReactions) => ({
        ...prevReactions,
        [messageId]: prevReactions[messageId] === reaction ? null : reaction,
      }));
    };
    return (
        <div key={message.id} className="flex items-start space-x-2">
          <div className="w-20 text-sm text-green-500">{message.name}</div>
          <div className="flex-1 border rounded-lg p-2">
            <p className="text-black dark:text-white">{message.output}</p>
            <small className="text-xs text-gray-500">{date}</small>
            <div className="mt-2 space-x-2">
              <button
                  className={`${currentReaction === "like" ? "text-xl" : ""}`}
                  onClick={() => handleReact(message.id, currentReaction === "like" ? null : "like")}
                  aria-label="Like"
              >
                👍 {/* Emoji Like */}
              </button>
              <button
                  className={`${currentReaction === "unlike" ? "text-xl" : ""}`}
                  onClick={() => handleReact(message.id, currentReaction === "unlike" ? null : "unlike")}
                  aria-label="unlike"
              >
                👎 {/* Emoji Félicitation */}
              </button>
            </div>
          </div>
        </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex flex-col w-4/5">
      <div className="flex-1 overflow-auto p-6">
        <div className="space-y-4">
          {messages.map((msg) => renderMessage(msg))}
        </div>
      </div>
      <div className="border-t p-4 bg-white dark:bg-gray-800">
        <div className="flex items-center space-x-2">
          <Input
            autoFocus
            className="flex-1"
            id="message-input"
            placeholder="Type a message"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyUp={(e) => {
              if (e.key === "Enter") {
                handleSendMessage("User"); // Envoie le message utilisateur lors de la touche "Entrée"
              }
            }}
          />
          <Button onClick={sendApiMessage}>Send</Button>
        </div>
      </div>
    </div>
  );
}
