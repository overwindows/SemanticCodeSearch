import AppsList from './apps-list'
import Error from './error'
import Loader from './loader'
import React, { useEffect, useState } from 'react'

// const computeSubscriptionsPrice = subscriptions =>
//   subscriptions.reduce((total, subscription) => total + subscription.price, 0)

const Content = () => {
  const [apps, setApps] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
  //   ;(async () => {
  //     const { json, requestError } = await apiRequest(apiGetApps, [])
  //     if (requestError) {
  //       setError(requestError)
  //     } else {
  //       const appsWithSubscriptionsPrice = json.map(app => ({
  //         subscriptionsPrice: computeSubscriptionsPrice(app.subscriptions),
  //         ...app,
  //       }))
  //       setApps(appsWithSubscriptionsPrice)
  //     }
  //     setIsLoading(false)
  //   })()
  }, [])

  if (isLoading) return <Loader />

  if (error) return <Error error={error} />

  return <AppsList apps={apps} />
}

export default Content
