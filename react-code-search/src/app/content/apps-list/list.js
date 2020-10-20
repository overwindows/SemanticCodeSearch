
import Highlighter from 'react-highlight-words'
import React, { useCallback, useEffect, useRef, useState } from 'react'
import styled from 'styled-components'
import { Button as MaterialButton } from '@material-ui/core';
import Popup from './popup';
import { js_beautify } from './beautify'
import { apiPostApps, apiRequest } from 'utils/requests'
import 'prismjs/themes/prism.css';

// DO NOT change the following lines to imports. auto organize imports will place them on top of Prism import, which is required by those
require('prismjs/components/prism-java');
require('prismjs/components/prism-python');
require('prismjs/components/prism-go');
require('prismjs/components/prism-ruby');
require('prismjs/components/prism-markup-templating.js');
require('prismjs/components/prism-clike.js');
require('prismjs/components/prism-c.js');
require('prismjs/components/prism-cpp.js');
require('prismjs/components/prism-php.js');
require('prismjs/plugins/line-highlight/prism-line-highlight');
require('prismjs/plugins/line-highlight/prism-line-highlight.css');
require('prismjs/plugins/line-numbers/prism-line-numbers');
require('prismjs/plugins/line-numbers/prism-line-numbers.css');

const Button = ({ onClick }) => (
  <MaterialButton
    style={{ marginTop: '1em', width: 'fit-content' }}
    onClick={onClick}
    variant="outlined"
    color="primary">
    Trans2Cpp
  </MaterialButton>
)

const AppContainer = styled.div`
  box-shadow: 0 2px 3px 0 ${({ theme }) => theme.colors.gray}, 0 0 3px 0 ${({ theme }) => theme.colors.gray};
  position: relative;
  width: 100%;
`

const AppTitle = styled.h1`
  color: ${({ theme }) => theme.primary};
`

const BoxInfo = styled.div`
  background-color: ${({ theme }) => theme.light};
  clear: both;
  cursor: pointer;
  flex: 1;
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  position: relative;
  transition: background-color 300ms ease-in-out;

  :hover {
    background-color: ${({ theme }) => theme.background}30;
  }
`

const BoxInfoContent = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  // overflow-x:auto;
`

const BoxInfoFooter = styled.div`
  display: flex;

  ul {
    display: inline-flex;
  }
  li {
    display: inline-flex;
    align-items: baseline;
    padding: 0 1rem 0 0;
  }
  li span {
    color: ${({ theme }) => theme.secondaryText};
  }
`

const Tags = styled.div`
  color: ${({ theme }) => theme.primary};
  font-weight: 400;
  text-align: right;
`

const App = ({ name, func, languages, scores, searchTerm }) => {

  const [isOpen, setIsOpen] = useState(false);
  const [content, setContent] = useState('');

  const togglePopup = useCallback(event => {
    (async () => {
      const { json, requestError } = await apiRequest(apiPostApps, [func])
      if (requestError) {
        // alert(requestError)
        // setError(requestError)
      } else {
        // const appsWithSubscriptionsPrice = json.map(app => ({
        //   subscriptionsPrice: computeSubscriptionsPrice(app.subscriptions),
        //   ...app,
        // }))
        // setSearchRes(appsWithSubscriptionsPrice)
        setIsOpen(!isOpen);
        setContent(json['cpp'][0])
        //alert(JSON.stringify(appsWithSubscriptionsPrice))
      }
      // setIsLoading(false)
    })()
  }, [func, setIsOpen, setContent])

  const togglePopupClose = useCallback(event => {
    // setPage(0)
    // setSearchTerm(event.target.value)
    // alert('Microsoft')
    setIsOpen(false);
    // description = 'Microsoft'
  }, [setIsOpen])

  var func_code = func
  if (languages == 'javascript') {
    func_code = js_beautify(func, { indent_size: 1, indent_char: " " })
  }

  return (
    <AppContainer>
      <BoxInfo>
        <BoxInfoContent>
          <div style={{ width: '1024px' }}>
            {/* <AppTitle>
              <Highlighter searchWords={[searchTerm]} textToHighlight={name} />
            </AppTitle> */}
            <p>
              <pre>
                <code class={`language-${languages}`} >
                  <Highlighter searchWords={[searchTerm]} textToHighlight={func_code} />
                </code>
              </pre>
            </p>
          </div>
          <Tags>{languages.sort().join(' / ')}</Tags>
        </BoxInfoContent>
        <BoxInfoFooter>
          <ul>
            {/* {scores.map(score => (
              <li key={score.name}>
                <span>{'Ranking Score'}</span>{' '}
                <h3>
                  {score.score > 0.0 ? (
                    <>
                      {(score.score).toFixed(5)}
                      <sup>{}</sup>
                    </>
                  ) : (
                      <>
                        {'Free'}
                        <sup />
                      </>
                    )}
                </h3>
              </li>
            ))} */}
          </ul>
        </BoxInfoFooter>
        {languages == 'python' && <Button onClick={togglePopup} />}
      </BoxInfo>
      {isOpen && <Popup id='code'
        content={content}
        handleClose={togglePopupClose}
      />}
    </AppContainer>

  )
}

const AppsList = ({ apps, searchTerm }) => (
  <ul>
    {apps.map(app => (
      <li key={app.id}>
        <App searchTerm={searchTerm} {...app} />
      </li>
    ))}
  </ul>
)

export default AppsList
