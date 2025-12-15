import React, { useState, useEffect } from 'react'
import { format, formatDistanceToNow, isPast } from 'date-fns'
import { dashboardService } from '../services/dashboard'
import { MessageSquare, Mail, CheckSquare, Star, AlertCircle, Clock, RefreshCw } from 'lucide-react'

export default function Dashboard() {
  const [items, setItems] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [filter, setFilter] = useState('all') // all, unread, important, overdue
  const [sortBy, setSortBy] = useState('priority_score')

  const loadData = async () => {
    try {
      setLoading(true)
      const [itemsData, statsData] = await Promise.all([
        dashboardService.getItems({ sort_by: sortBy }),
        dashboardService.getStats(),
      ])
      setItems(itemsData.items || [])
      setStats(statsData)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
    // Auto-refresh every 5 minutes
    const interval = setInterval(loadData, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [sortBy])

  const handleSync = async () => {
    setSyncing(true)
    try {
      await dashboardService.sync()
      setTimeout(() => {
        loadData()
        setSyncing(false)
      }, 2000)
    } catch (error) {
      console.error('Error syncing:', error)
      setSyncing(false)
    }
  }

  const handleUpdateItem = async (itemId, updates) => {
    try {
      await dashboardService.updateItem(itemId, updates)
      loadData()
    } catch (error) {
      console.error('Error updating item:', error)
    }
  }

  const getSourceIcon = (source) => {
    switch (source) {
      case 'slack':
        return <MessageSquare size={16} />
      case 'email':
        return <Mail size={16} />
      case 'jira':
        return <CheckSquare size={16} />
      default:
        return null
    }
  }

  const getSourceColor = (source) => {
    switch (source) {
      case 'slack':
        return '#4A154B'
      case 'email':
        return '#EA4335'
      case 'jira':
        return '#0052CC'
      default:
        return '#666'
    }
  }

  const getPriorityColor = (score) => {
    if (score >= 8) return '#dc3545'
    if (score >= 5) return '#ffc107'
    return '#28a745'
  }

  const filteredItems = items.filter((item) => {
    if (filter === 'unread') return item.status === 'unread'
    if (filter === 'important') return item.is_important
    if (filter === 'overdue')
      return item.deadline && isPast(new Date(item.deadline)) && item.status !== 'completed'
    return true
  })

  if (loading && !stats) {
    return <div style={styles.loading}>Loading...</div>
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1>Unified Dashboard</h1>
        <button onClick={handleSync} disabled={syncing} style={styles.syncButton}>
          <RefreshCw size={18} style={{ marginRight: '8px', animation: syncing ? 'spin 1s linear infinite' : 'none' }} />
          {syncing ? 'Syncing...' : 'Sync Now'}
        </button>
      </div>

      {stats && (
        <div style={styles.stats}>
          <div style={styles.statCard}>
            <div style={styles.statValue}>{stats.total_items}</div>
            <div style={styles.statLabel}>Total Items</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statValue}>{stats.unread_items}</div>
            <div style={styles.statLabel}>Unread</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statValue}>{stats.important_items}</div>
            <div style={styles.statLabel}>Important</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statValue}>{stats.overdue_items}</div>
            <div style={styles.statLabel}>Overdue</div>
          </div>
        </div>
      )}

      <div style={styles.filters}>
        <button
          onClick={() => setFilter('all')}
          style={{ ...styles.filterButton, ...(filter === 'all' ? styles.filterActive : {}) }}
        >
          All
        </button>
        <button
          onClick={() => setFilter('unread')}
          style={{ ...styles.filterButton, ...(filter === 'unread' ? styles.filterActive : {}) }}
        >
          Unread
        </button>
        <button
          onClick={() => setFilter('important')}
          style={{ ...styles.filterButton, ...(filter === 'important' ? styles.filterActive : {}) }}
        >
          Important
        </button>
        <button
          onClick={() => setFilter('overdue')}
          style={{ ...styles.filterButton, ...(filter === 'overdue' ? styles.filterActive : {}) }}
        >
          Overdue
        </button>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          style={styles.sortSelect}
        >
          <option value="priority_score">Priority</option>
          <option value="deadline">Deadline</option>
          <option value="created_at">Newest</option>
          <option value="user_rank">User Rank</option>
        </select>
      </div>

      <div style={styles.itemsList}>
        {filteredItems.length === 0 ? (
          <div style={styles.empty}>No items found</div>
        ) : (
          filteredItems.map((item) => (
            <div key={item.id} style={styles.itemCard}>
              <div style={styles.itemHeader}>
                <div style={styles.itemSource}>
                  <span
                    style={{
                      ...styles.sourceBadge,
                      backgroundColor: getSourceColor(item.source),
                    }}
                  >
                    {getSourceIcon(item.source)}
                    <span style={{ marginLeft: '6px' }}>{item.source.toUpperCase()}</span>
                  </span>
                  {item.is_starred && <Star size={16} fill="#ffc107" color="#ffc107" />}
                  {item.is_important && <AlertCircle size={16} color="#dc3545" />}
                </div>
                <div style={styles.itemActions}>
                  <span
                    style={{
                      ...styles.priorityBadge,
                      backgroundColor: getPriorityColor(item.priority_score),
                    }}
                  >
                    Priority: {item.priority_score.toFixed(1)}
                  </span>
                  {item.user_rank && (
                    <span style={styles.rankBadge}>Rank: {item.user_rank}</span>
                  )}
                </div>
              </div>

              <h3 style={styles.itemTitle}>{item.title}</h3>
              {item.content && (
                <p style={styles.itemContent}>
                  {item.content.length > 200 ? `${item.content.substring(0, 200)}...` : item.content}
                </p>
              )}

              <div style={styles.itemMeta}>
                {item.sender && (
                  <span style={styles.metaItem}>From: {item.sender}</span>
                )}
                {item.deadline && (
                  <span
                    style={{
                      ...styles.metaItem,
                      color: isPast(new Date(item.deadline)) ? '#dc3545' : '#666',
                    }}
                  >
                    <Clock size={14} style={{ marginRight: '4px' }} />
                    {isPast(new Date(item.deadline))
                      ? `Overdue: ${format(new Date(item.deadline), 'MMM d, yyyy')}`
                      : `Due: ${format(new Date(item.deadline), 'MMM d, yyyy')}`}
                  </span>
                )}
                <span style={styles.metaItem}>
                  {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                </span>
              </div>

              <div style={styles.itemFooter}>
                <div style={styles.statusButtons}>
                  <button
                    onClick={() =>
                      handleUpdateItem(item.id, {
                        status: item.status === 'unread' ? 'read' : 'unread',
                      })
                    }
                    style={styles.actionButton}
                  >
                    {item.status === 'unread' ? 'Mark Read' : 'Mark Unread'}
                  </button>
                  <button
                    onClick={() =>
                      handleUpdateItem(item.id, {
                        is_starred: !item.is_starred,
                      })
                    }
                    style={styles.actionButton}
                  >
                    {item.is_starred ? 'Unstar' : 'Star'}
                  </button>
                  <button
                    onClick={() =>
                      handleUpdateItem(item.id, {
                        is_important: !item.is_important,
                      })
                    }
                    style={styles.actionButton}
                  >
                    {item.is_important ? 'Unmark Important' : 'Mark Important'}
                  </button>
                  <button
                    onClick={() =>
                      handleUpdateItem(item.id, {
                        status: 'completed',
                      })
                    }
                    style={styles.actionButton}
                  >
                    Complete
                  </button>
                </div>
                {item.source_url && (
                  <a
                    href={item.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={styles.viewButton}
                  >
                    View Original
                  </a>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '2rem',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '2rem',
  },
  syncButton: {
    display: 'flex',
    alignItems: 'center',
    padding: '0.5rem 1rem',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  stats: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '1rem',
    marginBottom: '2rem',
  },
  statCard: {
    backgroundColor: 'white',
    padding: '1.5rem',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    textAlign: 'center',
  },
  statValue: {
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#007bff',
  },
  statLabel: {
    color: '#666',
    marginTop: '0.5rem',
  },
  filters: {
    display: 'flex',
    gap: '1rem',
    marginBottom: '1.5rem',
    alignItems: 'center',
  },
  filterButton: {
    padding: '0.5rem 1rem',
    border: '1px solid #ddd',
    backgroundColor: 'white',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  filterActive: {
    backgroundColor: '#007bff',
    color: 'white',
    borderColor: '#007bff',
  },
  sortSelect: {
    padding: '0.5rem',
    border: '1px solid #ddd',
    borderRadius: '4px',
    marginLeft: 'auto',
  },
  itemsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  itemCard: {
    backgroundColor: 'white',
    padding: '1.5rem',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  itemHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem',
  },
  itemSource: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  sourceBadge: {
    display: 'flex',
    alignItems: 'center',
    padding: '0.25rem 0.75rem',
    borderRadius: '4px',
    color: 'white',
    fontSize: '0.875rem',
    fontWeight: '500',
  },
  itemActions: {
    display: 'flex',
    gap: '0.5rem',
    alignItems: 'center',
  },
  priorityBadge: {
    padding: '0.25rem 0.75rem',
    borderRadius: '4px',
    color: 'white',
    fontSize: '0.875rem',
    fontWeight: '500',
  },
  rankBadge: {
    padding: '0.25rem 0.75rem',
    backgroundColor: '#6c757d',
    color: 'white',
    borderRadius: '4px',
    fontSize: '0.875rem',
  },
  itemTitle: {
    fontSize: '1.25rem',
    marginBottom: '0.5rem',
    color: '#333',
  },
  itemContent: {
    color: '#666',
    marginBottom: '1rem',
    lineHeight: '1.5',
  },
  itemMeta: {
    display: 'flex',
    gap: '1rem',
    marginBottom: '1rem',
    fontSize: '0.875rem',
    color: '#666',
    flexWrap: 'wrap',
  },
  metaItem: {
    display: 'flex',
    alignItems: 'center',
  },
  itemFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: '1rem',
    borderTop: '1px solid #eee',
  },
  statusButtons: {
    display: 'flex',
    gap: '0.5rem',
    flexWrap: 'wrap',
  },
  actionButton: {
    padding: '0.5rem 1rem',
    border: '1px solid #ddd',
    backgroundColor: 'white',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.875rem',
  },
  viewButton: {
    padding: '0.5rem 1rem',
    backgroundColor: '#007bff',
    color: 'white',
    textDecoration: 'none',
    borderRadius: '4px',
    fontSize: '0.875rem',
  },
  empty: {
    textAlign: 'center',
    padding: '3rem',
    color: '#666',
  },
  loading: {
    textAlign: 'center',
    padding: '3rem',
  },
}
