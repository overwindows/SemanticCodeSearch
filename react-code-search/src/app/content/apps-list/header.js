import React, { useCallback, useEffect, useRef } from 'react'
import styled from 'styled-components'
import { Cancel as CancelIcon } from 'assets/icons'
import { Search as SearchIcon } from 'assets/icons'
import { apiGetApps, apiRequest } from 'utils/requests'

const StyledHeader = styled.header`
  display: flex;
  position: relative;
  text-align: center;
  margin-bottom: 1.5rem;
`

const StyledInput = styled.input`
  background-clip: padding-box;
  border: 1px solid ${({ theme }) => theme.colors.grayLight};
  font-size: 1rem;
  font-weight: 300;
  padding: 1rem;
  resize: none;
  transition: all 300ms ease-in-out;
  width: 100%;
  -webkit-appearance: none;

  :focus,
  :hover {
    border: 1px solid ${({ theme }) => theme.primary};
    box-shadow: none;
    cursor: auto;
    outline: none;
  }
`

const computeSubscriptionsPrice = subscriptions =>
  subscriptions.reduce((total, subscription) => total + subscription.price, 0)

const CancelButton = styled(props => (
  <button title="Clear search" type="button" {...props}>
    <CancelIcon />
  </button>
))`
  width: 1.1rem;
  height: 1.1rem;
  padding: 0.1rem;
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  fill: ${({ theme }) => theme.primaryText}50;
`

const SearchButton = styled(props => (
  <button title="Clear search" type="button" {...props}>
    <SearchIcon />
  </button>
))`
  width: 1.1rem;
  height: 1.1rem;
  padding: 0.1rem;
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  fill: ${({ theme }) => theme.primaryText}50;
`

const Header = ({ searchTerm, setPage, setSearchTerm, setSearchRes, setIsSearch}) => {
  const inputRef = useRef(null)

  useEffect(() => inputRef.current.focus(), [])

  const onSearchTermChange = useCallback(
    event => {
      setPage(0)
      setSearchTerm(event.target.value)
      setIsSearch(false)
    },
    [setPage, setSearchTerm, setIsSearch]
  )

  const onCancelButtonClick = useCallback(() => {
    setSearchTerm('')
    inputRef.current.focus()
  }, [setSearchTerm])

  const onSearchButtonClick = useCallback(() => {
    (async () => {
      const { json, requestError } = await apiRequest(apiGetApps, [searchTerm])
      if (requestError) {
        // setError(requestError)
      } else {
        const appsWithSubscriptionsPrice = json.map(app => ({
          subscriptionsPrice: computeSubscriptionsPrice(app.subscriptions),
          ...app,
        }))
        setSearchRes(appsWithSubscriptionsPrice)
        //alert(JSON.stringify(appsWithSubscriptionsPrice))
      }
      // setIsLoading(false)
      setIsSearch(true)
    })()
    inputRef.current.focus()
    
  }, [searchTerm, setSearchRes, setIsSearch])

  return (
    <StyledHeader>
      <StyledInput
        onChange={onSearchTermChange}
        placeholder="Search by Query"
        ref={inputRef}
        title="Search for code"
        value={searchTerm}
      />
      {searchTerm && <CancelButton onClick={onCancelButtonClick} /> && <SearchButton onClick={onSearchButtonClick} />}
    </StyledHeader>
  )
}

export default Header
