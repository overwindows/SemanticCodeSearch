import React, { useCallback } from 'react'
import config from 'config'
import styled from 'styled-components'

const Nav = styled.nav`
  flex: 1 100%;
  padding: 1rem;
  order: 1;

  @media (min-width: ${({ theme }) => theme.screens.mobile}px) {
    flex: 0;
  }
`

const ListItem = styled(({ active, children, onClick, ...props }) => (
  <li {...props}>
    <button disabled={active} onClick={onClick} type="button">
      {children}
    </button>
  </li>
))`
  cursor: pointer;
  position: relative;

  button {
    border-bottom: 1px solid ${({ theme }) => theme.colors.gray};
    color: ${({ theme }) => theme.primaryText};
    cursor: pointer;
    font-size: 17px;
    font-weight: 300;
    padding: 1rem;
    text-align: left;
    text-decoration: none;
    transition: background-color 300ms ease-in-out;
    width: 100%;

    :disabled {
      color: ${({ theme }) => theme.primary};
      cursor: initial;
    }
    :not([disabled]):hover {
      background-color: ${({ theme }) => theme.light};
    }
  }
`

const Category = ({ active, category, children, onClick, ...props }) => {
  const onCategoryClick = useCallback(() => onClick(category), [category, onClick])

  return (
    <ListItem active={active} onClick={onCategoryClick} {...props}>
      {children}
    </ListItem>
  )
}

const NavMenu = ({ activeCategory, categories, setActiveCategory, setPage }) => {
  const onCategoryClick = useCallback(
    category => {
      setActiveCategory(category)
      setPage(0)
      document.title = category ? `${category} - ${config.appName}` : config.appName
    },
    [setActiveCategory, setPage]
  )

  return (
    <Nav>
      <h2>{'CodeSearch'}</h2>
      <ul>
        <Category
          active={!activeCategory}
          onClick={onCategoryClick}
          title={activeCategory ? 'See all apps' : undefined}
        >
          {'All'}
        </Category>
        {categories.map(category => (
          <Category
            active={category === activeCategory}
            category={category}
            key={category}
            onClick={onCategoryClick}
            title={category !== activeCategory ? `See ${category} apps` : undefined}
          >
            {category}
          </Category>
        ))}
      </ul>
    </Nav>
  )
}

export default NavMenu
