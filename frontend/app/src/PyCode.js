import React, { useState } from 'react';
import './PyCode.css';

const PyCode = () => {
    const [code, setCode] = useState('');
    const [resultCode, setResultCode] = useState('');
    const [resultMessage, setResultMessage] = useState('');
  
    const postCode = async (message_type) => {
      try {
        //const response = await axios.post('http://localhost:8000/code', { code });
        const response = await fetch('http://localhost:8000/code/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ code: code , message_type: message_type})
        })
        if (!response.ok) {
            // If the response status is not OK (e.g., 4xx or 5xx), throw an error
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const res = await response.json();
        console.log(res);
        setResultMessage(res.message);
        console.log('result', res)
        setResultCode(res.code);
      } catch (error) {
        console.error('Error executing code:', error);
        setResultMessage(error.message);
        setResultCode(error.code);
      }
    };

    const handleButtonPress = (button_value) => {
      console.log('clicked button:', button_value)
      postCode(button_value);
      //res = await result.json()
    };

    return (
      <div className="app-container">
        <div className="button-box">
          <button onClick={() => handleButtonPress("execute_code")}>Run code</button>
          <button onClick={() => handleButtonPress("enhance")}>Enhance</button>
          <button onClick={() => handleButtonPress("add_logging")}>Add logging</button>
          <button onClick={() => handleButtonPress("find_bugs")}>Find bugs</button>
          <button onClick={() => handleButtonPress("fix_errors")}>Fix errors</button>
        </div>
        <div className="column-container">
          <div className="column code-column">
            <textarea value={code} onChange={(e) => setCode(e.target.value)} />
          </div>
          <div className="column text-column">
            <p>{resultCode}</p>
          </div>
          <div className="column text-column">
            <p>{resultMessage}</p>
          </div>
        </div>
      </div>
    );

    //return (
    //  <div>
    //    <div style={{ display: 'flex', flexDirection: 'row' }}>
    //      <div style={{ flexDirection: 'column'}}>
    //        <textarea value={code} onChange={(e) => setCode(e.target.value)} />
    //        <button onClick={executeCode}>Execute Code</button>
    //      </div>
    //      <div className='result-container'>
    //        {error && <div style={{ color: 'red' }}>Error: {error}</div>}
    //        {result && <div>Result: {result}</div>}
    //      </div>
    //    </div>
    //  </div>
    //);
  };
  
  export default PyCode;