import React from "react";
import './style.css';
import Highlighter from 'react-highlight-words'
import styled from 'styled-components'
import {js_beautify} from './beautify'
import Prism from 'prismjs/prism';

require('prismjs/themes/prism.css');
require('prismjs');


const Tags = styled.div`
  color: ${({ theme }) => theme.primary};
  font-weight: 400;
  text-align: right;
`

const BoxInfoContent = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;
`

const Popup = props => {

  var formatted_code = js_beautify(props.content, {indent_size: 4,indent_char: " "})

  React.useEffect(() => {
    setTimeout(() => Prism.highlightAll(), 0)
    }, [])

  return (
    <div className="popup-box">
      <div className="box">
        <span className="close-icon" onClick={props.handleClose}>x</span><br></br>
        <BoxInfoContent>
        <div style={{ width: '1024px' }}>
        <p>
          {/* <pre className="line-numbers"> */}
          <pre>
            <code className="language-cpp">
              {/* <ReactPrismjs language="cpp" source={formatted_code} /> */}
              {formatted_code}
            </code>
          </pre>
        </p>
        </div>
        <Tags>{'c++'}</Tags>
        </BoxInfoContent>
      </div>
    </div>
  );
};

export default Popup;