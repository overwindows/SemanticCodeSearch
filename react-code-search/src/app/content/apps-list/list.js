import Highlighter from 'react-highlight-words'
import React, { useCallback, useEffect, useRef, useState } from 'react'
import styled from 'styled-components'
import { Button as MaterialButton } from '@material-ui/core';
import Popup from './popup';
import { apiPostApps, apiRequest } from 'utils/requests'


const Button = ({ onClick }) => (
  <MaterialButton
    style={{ marginTop: '1em', width: 'fit-content' }}
    onClick={onClick}
    variant="outlined"
    color="primary">
    Translate
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

const App = ({ name, description, categories, subscriptions, searchTerm }) => {

  const [isOpen, setIsOpen] = useState(false);
  const [content, setContent] =  useState('');

  const togglePopup = useCallback(event => {
    (async () => {
      const { json, requestError } = await apiRequest(apiPostApps, [description])
      //alert(description)
      if (requestError) {
        // alert(requestError)
        // setError(requestError)
      } else {
        // const appsWithSubscriptionsPrice = json.map(app => ({
        //   subscriptionsPrice: computeSubscriptionsPrice(app.subscriptions),
        //   ...app,
        // }))
        // setSearchRes(appsWithSubscriptionsPrice)
        //alert(JSON.stringify(json))
        setIsOpen(!isOpen);
        setContent(JSON.stringify(json))
        //alert(JSON.stringify(appsWithSubscriptionsPrice))
      }
      // setIsLoading(false)
    })() 
  }, [description, setIsOpen, setContent])

  const togglePopupClose = useCallback(event => {
    // setPage(0)
    // setSearchTerm(event.target.value)
    alert('Microsoft')
    setIsOpen(false);
    // description = 'Microsoft'
  }, [setIsOpen])

  return (
    <AppContainer>
      <BoxInfo>
        <BoxInfoContent>
          <div>
            <AppTitle>
              <Highlighter searchWords={[searchTerm]} textToHighlight={name} />
            </AppTitle>
            <p>
              <Highlighter searchWords={[searchTerm]} textToHighlight={description} />
            </p>
          </div>
          <Tags>{categories.sort().join(' / ')}</Tags>
        </BoxInfoContent>
        <BoxInfoFooter>
          <ul>
            {subscriptions.map(subscription => (
              <li key={subscription.name}>
                <span>{subscription.name}</span>{' '}
                <h3>
                  {subscription.price > 0 ? (
                    <>
                      {(subscription.price / 100).toFixed(2)}
                      <sup>{'€'}</sup>
                    </>
                  ) : (
                      <>
                        {'Free'}
                        <sup />
                      </>
                    )}
                </h3>
              </li>
            ))}
          </ul>
        </BoxInfoFooter>
        <Button onClick={togglePopup} />
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
