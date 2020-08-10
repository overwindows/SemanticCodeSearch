import React, { useState } from 'react';
import Button from './components/Button';
import SelectBox from './components/SelectBox';
import TextBox from './components/TextBox';
import './styles.scss';
import { postGenerateTextEndpoint } from './utils';
import {js_beautify} from './beautify';

function App() {
  const [text, setText] = useState("");
  const [model, setModel] = useState('gpt2');
  const [generatedText, postGenerateText] = postGenerateTextEndpoint();

  const generateText = () => {
    postGenerateText({ text, model, userId: 1 });
  }

  return (
    <div className='app-container'>
      <form noValidate autoComplete='off'>
        <h1>Patch Generation Demo</h1>
        <SelectBox model={model} setModel={setModel} />
        <TextBox text={text} setText={setText} />
        <Button onClick={generateText} />
      </form>

      {generatedText.pending &&
        <div className='result pending'>Please wait</div>}

      {generatedText.complete &&
        (generatedText.error ?
          <div className='result error'>Bad Request</div> :
          <div className='result valid'>
            {<div>
            {
              js_beautify(generatedText.data.result, {
                indent_size: 1,
                indent_char: " "
              })
            }
          </div>}
          </div>)}
    </div>
  );
}

export default App;
