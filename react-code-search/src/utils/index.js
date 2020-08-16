import { apiGetApps, apiPostApps, apiRequest } from './requests'
export { apiGetApps, apiPostApps, apiRequest }

export const paginateRecords = (records, currentPage, recordsPerPage) =>
  records.slice(currentPage * recordsPerPage, currentPage * recordsPerPage + recordsPerPage)
