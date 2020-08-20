import React from "react";
import './style.css';
import Highlighter from 'react-highlight-words'
require('prismjs/themes/prism.css');
require('prismjs');

const Popup = props => {
  return (
    <div className="popup-box">
      <div className="box">
        <span className="close-icon" onClick={props.handleClose}>x</span>
        <p>
          <pre>
            <code className="language-cpp">
              {props.content}
            </code>
          </pre>
        </p>
      </div>
    </div>
  );
};

export default Popup;