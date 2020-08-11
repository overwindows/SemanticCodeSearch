import React, { useCallback, useMemo } from 'react'
import config from 'config'
import styled from 'styled-components'

const StyledPagination = styled.ul`
  width: 100%;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  order: 3;
  padding-left: 0;
  margin-bottom: 1.5rem;
  text-align: center;
`

const StyledPaginationItem = styled(({ active, children, disabled, ...props }) => (
  <li {...props}>
    <button disabled={disabled || active} type="button">
      {children}
    </button>
  </li>
))`
  margin: 0 0.125rem;

  button {
    color: ${({ theme }) => theme.secondaryText};
    font-size: 1rem;
    padding: 0.375rem 0.4375rem;
    text-decoration: none;
    transition: background-color 300ms ease-in-out;
    ${({ active, theme }) => active && `background: ${theme.primary};`}

    :disabled {
      color: ${({ active, theme }) => (active ? theme.light : `${theme.secondaryText}50`)};
    }
    :not([disabled]) {
      cursor: pointer;
    }
    :not([disabled]):hover {
      background: ${({ theme }) => theme.primary};
      color: ${({ theme }) => theme.light};
    }
  }
`

const PaginationItem = ({ children, onClick, page, ...props }) => {
  const onPaginationItemClick = useCallback(() => onClick(page), [onClick, page])

  return (
    <StyledPaginationItem onClick={onPaginationItemClick} {...props}>
      {children}
    </StyledPaginationItem>
  )
}

const Pagination = ({ count, page, setPage }) => {
  const pages = useMemo(() => [...Array(Math.ceil(count / config.paginationSize)).keys()], [count])

  const onPaginationItemClick = useCallback(
    page => {
      setPage(page)
    },
    [setPage]
  )

  const goToPreviousPage = useCallback(() => setPage(page - 1), [page, setPage])

  const goToNextPage = useCallback(() => setPage(page + 1), [page, setPage])

  return (
    <StyledPagination>
      <StyledPaginationItem
        disabled={page === 0}
        onClick={goToPreviousPage}
        title={page > 0 ? 'Go to the previous page' : undefined}
      >
        {'<'}
      </StyledPaginationItem>
      {pages.map(pageNumber => (
        <PaginationItem
          active={pageNumber === page}
          key={pageNumber}
          onClick={onPaginationItemClick}
          page={pageNumber}
          title={pageNumber !== page ? `Go to page ${pageNumber + 1}` : undefined}
        >
          {pageNumber + 1}
        </PaginationItem>
      ))}
      <StyledPaginationItem
        disabled={page === pages[pages.length - 1]}
        onClick={goToNextPage}
        title={page < pages[pages.length - 1] ? 'Go to the next page' : undefined}
      >
        {'>'}
      </StyledPaginationItem>
    </StyledPagination>
  )
}

export default Pagination
