import { useEffect } from "react";

import { sessionState, useChatSession } from "@chainlit/react-client";
import { Playground } from "./components/playground";
import { useRecoilValue } from "recoil";
import { LeftBar } from "./components/leftbar";

const userEnv = {};

function App() {
  const { connect } = useChatSession();
  const session = useRecoilValue(sessionState);
  useEffect(() => {
    if (session?.socket.connected) {
      return;
    }
    fetch("http://localhost:80/custom-auth")
      .then((res) => {
        return res.json();
      })
      .then((data) => {
        connect({
          userEnv,
          accessToken: `Bearer: ${data.token}`,
        });
      });
  }, [connect]);

  return (
    <>
      <div className="flex flex-row">
        <LeftBar />
        <Playground />
      </div>
    </>
  );
}

export default App;
